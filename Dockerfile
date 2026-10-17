# The image Roar AI's one-click "Launch Open WebUI" deploys. Pinned on purpose:
# an app redeploys from this file, so moving the tag moves every Open WebUI app
# that redeploys after it. Bump only to a version that has been tested.
# The slim build: no bundled local models — chat, documents, voice and speech
# all go through your Roar AI models instead.
FROM ghcr.io/open-webui/open-webui:v0.12.3-slim
