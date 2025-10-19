{{- define "eligibility.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "eligibility.fullname" -}}
{{- include "eligibility.name" . -}}
{{- end -}}
