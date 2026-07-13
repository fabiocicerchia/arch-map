# Basic Example

What it shows: generate a Mermaid diagram from a Terraform state file (no
cluster needed).

## Run

```sh
arch-map --tfstate sample.tfstate -o ARCHITECTURE.md
cat ARCHITECTURE.md
```

You should see a database, a bucket and a queue node in the output.
