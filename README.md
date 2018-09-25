# vistoq-terraform
Terraform templates to build the vistoq infra in GCP


Set of terraform resources to build the Vistoq Demo infrastructure in GCP. This project relies on VM images from here: https://github.com/nembery/vistoq-demo 

# To build this infrastructure:

1. Build the VMs from the vistoq-demo project and upload them as custom images in GCP
2. Customize your env by setting the following env variables:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=~/projects/vistoq/gcp_vistoq.json
export GCLOUD_KEYFILE_JSON=~/projects/vistoq/gcp_vistoq.json
export TF_VAR_sshkeyfile='~/.ssh/gcp_vistoq'
export TF_VAR_sshkey=$(cat ~/.ssh/gcp_vistoq)
export TF_VAR_sshkeypub=$(cat ~/.ssh/gcp_vistoq.pub)
export PANORAMA_PASSWORD='super-secret-yo'
```

3. Run terraform

```bash
terraform init
terraform plan
terraform apply
```

4. Wait about 5 minutes for panorama to come up
5. Run the config_panorama.py tool from the scripts dir

```bash
cd scripts
./configure_panorama.py
```

6. Vistoq, Panorama, Aframe, and Bootstrapper should now all be avialble in GCP. Check the GCE console for assigned IP addresses

