# Pre-reqs

This project depends on this project to build the infrastructure images

https://github.com/nembery/vistoq-demo 


# Running

You must first get your GCP Credentials file and download it to the machine where
you will run Terraform from.

Also, create an SSH Key for GCP

```bash
export GOOGLE_APPLICATION_CREDENTIALS=~/projects/vistoq/gcp_vistoq.json
export GCLOUD_KEYFILE_JSON=~/projects/vistoq/gcp_vistoq.json
export TF_VAR_sshkeyfile='~/.ssh/gcp_vistoq'
export TF_VAR_sshkey=$(cat ~/.ssh/gcp_vistoq)
export TF_VAR_sshkeypub=$(cat ~/.ssh/gcp_vistoq.pub)
export PANORAMA_PASSWORD='super-secret-yo'
```