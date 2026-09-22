# syntax=docker/dockerfile:1
#
# intertextual-hub: five components in one container — Apache, two gunicorn apps
# (Intertextual Hub and the embedded TopoLogic), PhiloLogic 4.6 as CGI, and PostgreSQL.
# All of them were customised for this site and none is interchangeable with the
# standalone `topologic` or `philologic4.7` services. See
# ../docker_containers_update/intertextual-hub/MIGRATION.md.
#
# This replaces a 162 GB image made by `docker commit` from a virtual machine, which is
# why the thing being removed here is not just data but an entire dormant operating
# system: systemd, snapd, sshd, ufw, cron, rsyslog, netplan, /etc/fstab.

# ---------------------------------------------------------------------------------------
# 0. The other three upstreams, at exactly the commits this deployment runs.
#    Fetched rather than vendored: COPY cannot reach outside the build context, and the
#    weekly loop runs `docker build <context>` with no prepare step, so a submodule or a
#    populate-script would silently build the wrong thing. Pinned to SHAs, so this is
#    deterministic despite being a network fetch — the same way text_preprocessing and the
#    spaCy model are already fetched below.
# ---------------------------------------------------------------------------------------
FROM ubuntu:26.04 AS sources
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# PhiloLogic 4.6 — the version these seven corpora were loaded with. NOT 4.7: moving there
# would mean reloading 102 GB, and no reload is planned.
ARG PHILOLOGIC_REF=f7f8cfc1044dd4a35d6d953c9344c5d0568bdfcc
RUN git clone --quiet https://github.com/ARTFL-Project/PhiloLogic4.git /philologic \
 && git -C /philologic checkout --quiet "$PHILOLOGIC_REF" \
 && rm -rf /philologic/.git

# The embedded TopoLogic, at TWO different commits, deliberately. The deployed library is
# b4d3b446 and the deployed API server is the later 91e2e210 — the library was never
# reinstalled after it, and building both from the later ref would change behaviour.
ARG TOPOLOGIC_LIB_REF=b4d3b44642ae0c9322694ec862901d39907ae736
ARG TOPOLOGIC_API_REF=91e2e2109b4a576a9c07a36512b0743c0e6e6c46
RUN git clone --quiet https://github.com/ARTFL-Project/TopoLogic.git /topologic-src \
 && git -C /topologic-src checkout --quiet "$TOPOLOGIC_LIB_REF" \
 && cp -a /topologic-src/lib /topologic-lib \
 && git -C /topologic-src checkout --quiet "$TOPOLOGIC_API_REF" \
 && cp -a /topologic-src/api /topologic-api \
 && cp -a /topologic-src/config /topologic-config \
 && cp -a /topologic-src/web-app /topologic-webapp \
 && rm -rf /topologic-src

# ---------------------------------------------------------------------------------------
# 1. PhiloLogic's C core.
#    2004-vintage C. GCC 14 made implicit function declarations an error rather than a
#    warning, so db/pack4 does not build on the stock toolchain — and pack4 is the LOADER,
#    which no smoke test of the running site would ever exercise. Found by T1; the fix is
#    a build flag, not a source change.
# ---------------------------------------------------------------------------------------
FROM ubuntu:26.04 AS philo-core
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential make libgdbm-dev libdb-dev \
 && rm -rf /var/lib/apt/lists/*
COPY --from=sources /philologic /philologic
RUN cd /philologic/libphilo \
 && make CFLAGS="-O3 -std=gnu17 -Wno-implicit-function-declaration" \
 && test -x db/corpus_search && test -x db/pack4

# ---------------------------------------------------------------------------------------
# 2. The Vue bundle.
#    Node 14 and node-sass 4.14, pinned because node-sass is a native libsass binding that
#    does not build on modern Node. This stage never ships. Migrating to dart-sass is the
#    right follow-up and is deliberately not done here.
#
#    API_SERVER is compiled INTO the bundle: main.js does `import appConfig from
#    "../../config/appConfig.json"`, so a staging image must be built with a staging origin
#    or it will call production while looking perfect. That is the dvlf lesson, and unlike
#    commonplaces this service really does have the trap.
# ---------------------------------------------------------------------------------------
FROM node:14 AS bundle
ARG API_SERVER=https://intertextual-hub.uchicago.edu
WORKDIR /build
COPY web-app/package.json ./web-app/
RUN cd web-app && npm install --no-audit --no-fund
COPY config ./config
COPY web-app ./web-app
RUN cd config \
 && python3 -c "import json,os,sys; p='appConfig.json'; d=json.load(open(p)); d['apiServer']=os.environ['API_SERVER']; json.dump(d,open(p,'w'),indent=4)" \
    2>/dev/null || sed -i "s#\"apiServer\":[^,]*,#\"apiServer\": \"${API_SERVER}\",#" appConfig.json
RUN cd web-app && npm run build && test -f dist/index.html

# ---------------------------------------------------------------------------------------
# 3. The Python environment.
#    CPython 3.8 from uv, not the distro. It is EOL, and that is a deliberate, recorded
#    trade: the artifacts this application loads are pinned to scikit-learn 0.23.2,
#    gensim 3.8.3 and spaCy 2.3.2, and 3.9 needs gensim 4, which breaks the API
#    explore_words.py calls. The security argument for this migration is the base OS,
#    Apache, OpenSSL and the system libraries — all of which are current here.
# ---------------------------------------------------------------------------------------
FROM ubuntu:26.04 AS pyenv
ENV DEBIAN_FRONTEND=noninteractive UV_PYTHON_INSTALL_DIR=/opt/python UV_LINK_MODE=copy
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential libpq-dev git ca-certificates \
 && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY requirements.txt /tmp/requirements.txt
RUN uv venv /opt/venv --python 3.8 --managed-python \
 && VIRTUAL_ENV=/opt/venv uv pip install --no-cache -r /tmp/requirements.txt \
 # Not on PyPI: an ARTFL package. Pinned to the commit the deployed 0.8.2 is byte-identical
 # to. similar_docs.py imports PreProcessor from it at module scope.
 && VIRTUAL_ENV=/opt/venv uv pip install --no-cache \
      "text_preprocessing @ git+https://github.com/ARTFL-Project/text-preprocessing.git@3ec11a7c8bc9ddba7fbcc7bbe88960141eda3836" \
 # The French model, from a GitHub release rather than PyPI...
 && VIRTUAL_ENV=/opt/venv uv pip install --no-cache \
      "https://github.com/explosion/spacy-models/releases/download/fr_core_news_lg-2.3.0/fr_core_news_lg-2.3.0.tar.gz" \
 # ...and the shortcut link it needs. text_preprocessing maps "french" -> "fr" and calls
 # spacy.load("fr"), which is a spaCy 2.x SHORTCUT, not a package name. Installing the
 # model is not enough; without this the app dies at import with OSError E050. The old
 # image had it because someone ran `spacy link` in 2020.
 && ln -sfn /opt/venv/lib/python3.8/site-packages/fr_core_news_lg \
            /opt/venv/lib/python3.8/site-packages/spacy/data/fr \
 && rm -rf /root/.cache
# PhiloLogic's own Python package, from the same source the C core was built from.
COPY --from=sources /philologic /philologic
# uv creates venvs without pip, so this installs with uv too. philologic 4.6's setup.py
# still does `from distutils.core import setup`, which is fine on 3.8 and would not be on
# 3.12+ — one more small thing anchoring this image to the interpreter it has.
RUN cd /philologic/python && VIRTUAL_ENV=/opt/venv uv pip install --no-cache . \
 && /opt/venv/bin/python -c "from philologic.runtime.DB import DB; from philologic.runtime.get_text import get_text"

# The embedded TopoLogic library, at the commit the deployed copy is byte-identical to.
# It belongs here rather than in the final stage because that stage has no uv and uv
# creates venvs without pip.
COPY --from=sources /topologic-lib /tmp/topologic-lib
# --no-deps: its install_requires names nltk, which this container never uses (it is for
# the modelling side), and an older text_preprocessing pin than the one installed above.
# Everything else it needs is already pinned in requirements.txt.
RUN cd /tmp/topologic-lib && VIRTUAL_ENV=/opt/venv uv pip install --no-cache --no-deps . \
 && /opt/venv/bin/python -c "import topologic" \
 && rm -rf /tmp/topologic-lib
# uv's CPython ships its own pip and setuptools, and the venv has its own copies. The
# interpreter-level ones are never used — the venv is built here, once — and they are two
# more findings in the weekly scan that could never be actioned.
#
# The venv's setuptools STAYS: scikit-learn 0.23.2 imports pkg_resources at runtime, which
# comes from it. Its vendored setuptools/_vendor/{wheel,jaraco.*} are reported by Trivy
# because they carry dist-info directories, but they are not installed packages and are
# unreachable unless setuptools imports them. They are left alone rather than deleted:
# removing a dist-info to quiet a scanner is not a fix, and a report people learn to game
# is worse than a report with an explained finding in it.
RUN rm -rf /opt/python/cpython-*/lib/python3.8/site-packages/pip \
           /opt/python/cpython-*/lib/python3.8/site-packages/pip-*.dist-info \
           /opt/python/cpython-*/lib/python3.8/site-packages/setuptools \
           /opt/python/cpython-*/lib/python3.8/site-packages/setuptools-*.dist-info \
           /opt/python/cpython-*/lib/python3.8/site-packages/pkg_resources

# ---------------------------------------------------------------------------------------
# 4. The image that ships.
# ---------------------------------------------------------------------------------------
FROM ubuntu:26.04

# The databases collate under en_US.UTF-8 — a glibc collation, not byte-order C.UTF-8 — so
# initdb must be told explicitly and the locale must exist. ubuntu:26.04 does not ship it.
ENV DEBIAN_FRONTEND=noninteractive LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

ARG REBUILD_DATE=unset
RUN echo "rebuild: $REBUILD_DATE" \
 && apt-get update && apt-get install -y --no-install-recommends \
      apache2 postgresql postgresql-contrib locales ca-certificates libgdbm6t64 \
 && locale-gen en_US.UTF-8 && update-locale LANG=en_US.UTF-8 \
 && rm -rf /var/lib/apt/lists/* \
 # The Debian package runs initdb at install time and leaves a cluster this image never
 # uses. The old image carried a second, empty postmaster for years for exactly this reason.
 && rm -rf /var/lib/postgresql/18/main \
 && rm -f /usr/bin/pebble \
 && rm -f /etc/ssl/private/ssl-cert-snakeoil.key /etc/ssl/certs/ssl-cert-snakeoil.pem \
 # PhiloLogic needs cgid and rewrite; the vhost needs proxy_http, headers and remoteip.
 && a2enmod rewrite cgid proxy proxy_http deflate headers remoteip \
 && a2dissite 000-default \
 # Apache's packaged logs are symlinks to files in the image. Everything goes to the
 # container runtime instead; the old image reached 9.9 GB here because logrotate is driven
 # by cron and nothing starts cron in a container.
 && rm -rf /var/log/apache2 && mkdir -p /var/log/apache2

# initdb calls getpwuid(), so the runtime uid must exist. 483 matches a real host account,
# so `ps` and `ls -l` agree on both sides. Nothing in this image is ever root: there is no
# gosu and no runtime privilege drop, which is why the compose file needs no cap_add.
RUN groupadd -r -g 483 intertextual-hub \
 && useradd -r -u 483 -g 483 -M -d /nonexistent -s /usr/sbin/nologin intertextual-hub

COPY --from=pyenv /opt/python /opt/python
COPY --from=pyenv /opt/venv   /opt/venv
COPY --from=philo-core /philologic/libphilo/db/corpus_search /bin/corpus_search
COPY --from=philo-core /philologic/libphilo/db/pack4         /bin/pack4
COPY --from=sources /philologic/www /var/lib/philologic4/web_app
RUN mkdir -p /etc/philologic \
 && printf "database_root = '/var/www/html/philologic/'\nurl_root = 'https://intertextual-hub.uchicago.edu/philologic/'\nweb_app_dir = '/var/lib/philologic4/web_app/'\ntheme = '/var/lib/philologic4/web_app/app/assets/css/split/default_theme.css'\n" \
    > /etc/philologic/philologic4.cfg

# The embedded TopoLogic. Two different commits, deliberately: the deployed library is
# b4d3b446 (2020-10-09) and the deployed API server is the later 91e2e210 (2020-11-03) —
# the library was never reinstalled after it. Building both from the later ref would
# change behaviour.
COPY --from=sources /topologic-api     /var/lib/topologic/api
COPY --from=sources /topologic-config  /var/lib/topologic/config
COPY --from=sources /topologic-webapp  /var/lib/topologic/web-app
COPY deploy/topologic-web_server.sh           /var/lib/topologic/api_server/web_server.sh

# Apache
COPY deploy/apache-ports.conf /etc/apache2/ports.conf
COPY deploy/apache-vhost.conf /etc/apache2/sites-available/intertextual-hub.conf
RUN a2ensite intertextual-hub

# The application. config/appConfig.json is tracked and ships; db_config.json and
# logins.txt arrive only as read-only bind mounts and are never in this image.
WORKDIR /var/www/html/intertextual_hub/Intertextual-Hub-App
COPY api                        ./api
COPY api_server/web_server.sh   ./api_server/web_server.sh
COPY config/appConfig.json      ./config/appConfig.json
COPY --from=bundle /build/web-app/dist ./web-app/dist
# Read at import time by similar_docs.py, via an absolute path. Site-local: it is in no
# upstream repository and existed only inside the old container until this migration.
COPY deploy/site-config/stopwords.txt /var/www/html/intertextual_hub/config/stopwords.txt

COPY entrypoint.sh /entrypoint.sh

ENV PATH=/opt/venv/bin:/usr/lib/postgresql/18/bin:$PATH \
    PGDATA=/data/psql/18 \
    PGHOST=/tmp \
    PYTHONUNBUFFERED=1 \
    HOME=/tmp \
    APACHE_RUN_USER=intertextual-hub \
    APACHE_RUN_GROUP=intertextual-hub \
    APACHE_PID_FILE=/tmp/apache2.pid \
    APACHE_RUN_DIR=/tmp/apache-run \
    APACHE_LOCK_DIR=/tmp/apache-lock \
    APACHE_LOG_DIR=/tmp/apache-log

USER 483:483
EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
