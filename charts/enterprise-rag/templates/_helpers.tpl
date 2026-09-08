{{- define "enterprise-rag.name" -}}
enterprise-rag
{{- end }}

{{- define "enterprise-rag.fullname" -}}
{{ .Release.Name }}-{{ include "enterprise-rag.name" . }}
{{- end }}

{{- define "enterprise-rag.labels" -}}
app.kubernetes.io/name: {{ include "enterprise-rag.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}
