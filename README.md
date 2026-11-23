# CityFlow | CS 4218/5218, Group 6

The D1 demo sends real NYC taxi trips from an OKE Job to the six-partition `trips` topic. A consumer on OKE reads them back.

- `project.auto.tfvars` holds the CityFlow settings for the course Terraform scaffold.
- `replayer/` publishes the trips, and `d1_printer/d1_printer.py` reads and prints them.
- `k8s/` holds the ConfigMap and both Jobs.

## 1. Provision OCI resources

Use the course Terraform scaffold. Copy `project.auto.tfvars` into a new scaffold or merge its settings into your team's existing configuration. Use the existing Terraform state for an existing deployment.

```bash
cd ~/terraform-scaffold
terraform init
terraform plan
terraform apply
terraform output
```

Run the scaffold's `kubeconfig_command` to connect to OKE.

## 2. Prepare trip input

In Cloud Shell, download the source file from the course bucket.

```bash
oci os object get -bn 4218-datasets \
  --name nyc-tlc/yellow_tripdata_2025-01.parquet --file yellow_tripdata_2025-01.parquet
```

Select five trips from one pickup day, sort them by pickup time, and save them as `replayer/input/trips.tsv` where you build the image. Each line is the pickup zone, a tab, and a JSON object with `run_id`, `event_id`, `pickup_ts` (UTC), `pickup_zone`, `dropoff_zone`, and `fare_cents`. The replayer adds `sent_at` in Unix seconds.

## 3. Build and push to OCIR

Run from the repository root on a machine with Docker. Replace `<namespace>` with the Object Storage namespace and use your own OCI auth token when `docker login` prompts for a password. The login username is `<namespace>/<username>` (include your domain if your OCI login requires it).

```bash
docker login ord.ocir.io
docker buildx create --use --name multi 2>/dev/null || docker buildx use multi
REPLAYER_IMAGE='ord.ocir.io/<namespace>/4218-team6/replayer:d1'
PRINTER_IMAGE='ord.ocir.io/<namespace>/4218-team6/processor:d1-printer'
docker buildx build --platform linux/arm64,linux/amd64 -t "$REPLAYER_IMAGE" --push replayer
docker buildx build --platform linux/arm64,linux/amd64 -t "$PRINTER_IMAGE" --push d1_printer
```

## 4. Run both images on OKE from Cloud Shell

In Cloud Shell, use the namespace and `ocir-secret` from the course setup. In that namespace, create the Kafka Secret once. Get `BOOTSTRAP` and `KAFKA_USER` from the team's Kafka Connection Settings.

```bash
kubectl config set-context --current --namespace=dev-$USER
read -rp 'Kafka bootstrap server: ' BOOTSTRAP
read -rp 'Kafka username: ' KAFKA_USER
read -rs -p 'Auth token: ' KAFKA_PASS; echo
kubectl create secret generic cityflow-kafka-auth \
  --from-env-file=<(printf 'BOOTSTRAP=%s\nKAFKA_USER=%s\nKAFKA_PASS=%s\n' "$BOOTSTRAP" "$KAFKA_USER" "$KAFKA_PASS")
unset KAFKA_PASS
```

From the repository root, replace the `image:` values in `k8s/d1-printer.yaml` and `k8s/replayer.yaml` with the images you pushed. Use new names for both Jobs on another run.

```bash
kubectl apply -f k8s/config.yaml
kubectl apply -f k8s/d1-printer.yaml
kubectl apply -f k8s/replayer.yaml
kubectl wait --for=condition=complete job/cityflow-replay --timeout=180s
kubectl wait --for=condition=complete job/cityflow-d1-printer --timeout=180s
kubectl logs job/cityflow-d1-printer
kubectl get pods -o wide
```

Paste the five consumer log lines and `kubectl get pods -o wide` into the D1 appendix.

AI assisted with documentation, Dockerfiles, Kubernetes manifests, the D1 printer script, and preparation of the five-trip demo sample.
