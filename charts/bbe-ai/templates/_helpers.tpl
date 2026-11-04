{{- define "bbe-ai.labels" -}}
app.kubernetes.io/name: bbe-ai
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{- define "bbe-ai.selectorLabels" -}}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/component: models
{{- end -}}

{{/*
The ports Home Assistant expects each service on, which its integrations suggest
*/}}
{{- define "bbe-ai.speechToTextPort" -}}10300{{- end -}}
{{- define "bbe-ai.textToSpeechPort" -}}10200{{- end -}}
{{- define "bbe-ai.ollamaPort" -}}11434{{- end -}}

{{/*
Ollama lists a model named without a tag as `<name>:latest`, which is how the setup finds it again
*/}}
{{- define "bbe-ai.ollamaModel" -}}
{{- $model := .Values.bbe.ai.ollama.model -}}
{{- if contains ":" $model -}}
{{- $model -}}
{{- else -}}
{{- printf "%s:latest" $model -}}
{{- end -}}
{{- end -}}

{{/*
Every container runs as a user with no capabilities, which `restricted` asks for
*/}}
{{- define "bbe-ai.containerSecurityContext" -}}
allowPrivilegeEscalation: false
capabilities:
  drop:
    - ALL
{{- end -}}

{{/*
Open WebUI only runs with Ollama, the model it chats with
*/}}
{{- define "bbe-ai.chatEnabled" -}}
{{- if and .Values.bbe.ai.chat.enabled .Values.bbe.ai.ollama.enabled }}true{{ end -}}
{{- end -}}

{{- define "bbe-ai.chatSelectorLabels" -}}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/component: open-webui
{{- end -}}
