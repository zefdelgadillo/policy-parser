# Policy Parser
Easily parse and filter yaml or json-based Google Cloud Platform (GCP) IAM policy documents.

```bash
$ gcloud projects get-iam-policy my-project | pparse -o table
principal_type    principal                                                                    role
----------------  ---------------------------------------------------------------------------  ------------------------------------
serviceAccount    555555555555@cloudbuild.gserviceaccount.com                                  roles/cloudbuild.builds.builder
group             tech-dev-team@company.com                                                    roles/cloudbuild.builds.editor
serviceAccount    service-555555555555@gcp-sa-cloudbuild.iam.gserviceaccount.com               roles/cloudbuild.serviceAgent
serviceAccount    service-555555555555@gcp-sa-computescanning.iam.gserviceaccount.com          roles/computescanning.serviceAgent
group             tech-dev-managers@company.com                                                roles/owner
user              annbaker@company.com                                                         roles/storage.admin
user              louiefranco@company.com                                                      roles/storage.admin
user              annbaker@company.com                                                         roles/storage.objectAdmin
user              louiefranco@company.com                                                      roles/storage.objectAdmin
group             tech-all@company.com                                                         roles/viewer
group             tech-dev-team@company.com                                                    roles/viewer
```

## Installation
```
# Requires Python >= 3.8
pip install pparse
```

## Usage
### Parse
Pass in a policy document into `pparse` directly from gcloud and select an output format using `--output-format`.

```bash 
$ gcloud projects get-iam-policy my-project | pparse --output-format csv
```
* csv
* table
* json
* yaml


### Filters
You can filter policy documents by using one of the following commands. Use the `-s` flag to return a simple list of users or roles.

#### Filter by User Principal: `pparse principal`
```bash
$ gcloud ... | pparse principal louiefranco@company.com -s
roles/owner
roles/storage.admin
roles/storage.objectAdmin
```

#### Filter by Role `pparse role`
```bash
$ gcloud ... | pparse role roles/owner -s
group:tech-code-guidance@company.com
group:tech-dev-managers@company.com
user:annbaker@company.com
user:jimmyjohn@company.com
user:louiefranco@company.com
user:rhondaseltzer@company.com
```

#### Filter by Domain `pparse domain`
```bash
$ gcloud ... | pparse domain company.com
bindings:
- members:
  - group:tech-dev-team@company.com
  role: roles/cloudbuild.builds.editor
- members:
  - group:tech-code-guidance@company.com
  - group:tech-dev-managers@company.com
  - user:annbaker@company.com
  - user:jimmyjohn@company.com
  - user:louiefranco@company.com
  - user:rhondaseltzer@company.com
  role: roles/owner
```

#### Filter by Principal Type `pparse type`
```bash
$ gcloud ... | pparse -o csv type serviceaccount
principal_type,principal,role
serviceAccount,555555555555@cloudbuild.gserviceaccount.com,roles/cloudbuild.builds.builder
serviceAccount,service-555555555555@gcp-sa-cloudbuild.iam.gserviceaccount.com,roles/cloudbuild.serviceAgent
serviceAccount,service-555555555555@compute-system.iam.gserviceaccount.com,roles/compute.serviceAgent
serviceAccount,service-555555555555@gcp-sa-computescanning.iam.gserviceaccount.com,roles/computescanning.serviceAgent
serviceAccount,service-555555555555@container-engine-robot.iam.gserviceaccount.com,roles/container.serviceAgent
```
