# The isolated content origin's own image, ADR-012 condition 5.
#
# Everything this origin serves from local disk is now exactly one thing: the
# h5p-standalone player bundle. It carries no ticket and needs no signed URL —
# useless without a content, condition 3's "frozen internal artefact" applies
# to it the same way it applies to a library, and the natural place for a
# frozen artefact is baked into the image that serves it, not a folder an
# operator has to remember to prepare on whichever machine runs this container.
#
# `content/` and `libraries/` do NOT live here: they come from the runtime
# bucket, fetched through a URL the API signs per request (see the nginx
# template and `app/api/v1/internal.py`). That split is what makes this image
# buildable and runnable anywhere — a laptop, Render, any platform that cannot
# share a disk between two services — without carrying a single byte of
# content in it.

FROM node:20-alpine AS player
WORKDIR /player
# `--no-save`: nothing here is a project of its own, just a place to let npm
# resolve one package so its `dist/` can be copied out.
RUN npm init -y >/dev/null 2>&1 && npm install --no-save h5p-standalone@3.8.2

FROM nginx:1.27-alpine
COPY --from=player /player/node_modules/h5p-standalone/dist/ /srv/content/player/
# The one part of this origin the project wrote itself, and the only one that
# decides what leaves it — see its own header comment for why.
COPY apps/api/app/content/page/play.html /srv/content/player/play.html
COPY infrastructure/nginx/content-origin.conf.template /etc/nginx/templates/default.conf.template
