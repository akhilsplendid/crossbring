{{- define "paymentservice.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "paymentservice.fullname" -}}
{{- include "paymentservice.name" . -}}
{{- end -}}
