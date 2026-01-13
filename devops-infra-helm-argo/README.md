devops-infra-helm-argo

Purpose  
Demonstrate GitOps for a multi-service stack using a Helm umbrella chart and ArgoCD ApplicationSet, with OpenShift build/route examples.

Structure  
- helm/umbrella: umbrella chart with bundled subcharts (caseservice, paymentservice, eligibility, citizen-portal)  
- helm/charts: vendored subcharts so the umbrella is self-contained  
- argo/: ArgoCD Application and ApplicationSet targeting this repo/umbrella chart  
- openshift/: imagestreams + buildconfigs and routes for OpenShift exposure

Prereqs  
- Helm 3  
- ArgoCD (if using GitOps)  
- Cluster namespaces: `social-dev`, `social-prod` (or adjust ApplicationSet)

Usage  
1) Helm direct: `helm dependency update ./helm/umbrella && helm upgrade --install sb-platform ./helm/umbrella -n social --create-namespace`  
2) ArgoCD single env: `kubectl apply -f argo/app-umbrella.yaml` (edit namespace if not `argocd`)  
3) ArgoCD dev+prod via ApplicationSet: `kubectl apply -f argo/appset-umbrella.yaml`  
4) OpenShift builds/routes: `oc apply -f openshift/imagestreams-buildconfigs.yaml && oc apply -f openshift/routes.yaml`

Notes  
- Update image repositories/tags in `helm/umbrella/values.yaml` (or override via ArgoCD/Helm values).  
- ArgoCD `repoURL` points to this repo (`https://github.com/akhilsplendid/devops-infra-helm-argo.git`); change branch/path as needed.  
- For private registries, set imagePullSecrets in subchart values or a global secret and wire it into the charts.
