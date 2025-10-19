devops-infra-helm-argo
Purpose: Demonstrate GitOps with Helm and ArgoCD, plus OpenShift specifics.

Structure
- helm/umbrella — umbrella chart values to deploy services together
- argo/ — ArgoCD Applications for each service and umbrella
- openshift/ — Route examples to expose services on OpenShift

Usage (examples)
- Helm umbrella: `helm upgrade --install sb-platform ./helm/umbrella -n social --create-namespace`
- ArgoCD: Apply the app YAMLs after setting `repoURL` and branch

Notes
- Replace `your-registry/*` images or set an imagePullSecret in values.
