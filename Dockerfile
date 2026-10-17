# The image Roar AI's one-click "Launch Open WebUI" deploys. Pinned on purpose:
# an app redeploys from this file, so moving the tag moves every Open WebUI app
# that redeploys after it. Bump only to a version that has been tested.
# The full build, not -slim: slim cannot read PDF, Word, Excel or PowerPoint
# uploads without a separate extractor service. Chat, document search, voice
# and speech still go through your Roar AI models.
FROM ghcr.io/open-webui/open-webui:v0.12.3
