{{- define "citizen-portal.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "citizen-portal.fullname" -}}
{{- include "citizen-portal.name" . -}}
{{- end -}}
