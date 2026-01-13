{{- define "caseservice.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "caseservice.fullname" -}}
{{- include "caseservice.name" . -}}
{{- end -}}
