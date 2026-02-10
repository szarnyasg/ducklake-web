---
layout: docu
title: Read-Only DuckLake from Cloudflare R2
---

This guide explains how to set up a public read-only DuckLake on Cloudflare R2.
Users can query this DuckLake through HTTPS without authentication and for free.
The owner of the DuckLake pays for the storage costs but pays only a negligible amount for serving requests (see the [Pricing section](#pricing) for more details).

## Steps

### Creating the Bucket

Create a [public Cloudflare R2 bucket](https://developers.cloudflare.com/r2/buckets/create-buckets/).

### Creating the DuckLake

Create a new DuckLake following the [“Using a Remove Data Path” guide]({% link docs/stable/duckdb/guides/using_a_remote_data_path.md %}) using DuckDB as the catalog database.

### Uploading the DuckLake

Upload the `.ducklake` file and its data directory to R2. We recommend using [Rclone](https://rclone.org/), which has built-in support for Cloudflare R2.

```bash
rclone config
```

Create a new Rclone remote (see the details in the foldouts below). In our examples, we will call this `⟨your_rclone_remote⟩`{:.language-sql .highlight}.

<details markdown='1'>
<summary markdown='span'>
Storage configuration in Rclone
</summary>
```text
Option Storage.
Type of storage to configure.
Choose a number from below, or type in your own value.
 1 / 1Fichier
   \ (fichier)
 2 / Akamai NetStorage
   \ (netstorage)
 3 / Alias for an existing remote
   \ (alias)
 4 / Amazon S3 Compliant Storage Providers including AWS, Alibaba, ArvanCloud, BizflyCloud, Ceph, ChinaMobile, Cloudflare, Cubbit, DigitalOcean, Dreamhost, Exaba, FileLu, FlashBlade, GCS, Hetzner, HuaweiOBS, IBMCOS, IDrive, Intercolo, IONOS, Leviia, Liara, Linode, LyveCloud, Magalu, Mega, Minio, Netease, Outscale, OVHcloud, Petabox, Qiniu, Rabata, RackCorp, Rclone, Scaleway, SeaweedFS, Selectel, Servercore, SpectraLogic, StackPath, Storj, Synology, TencentCOS, Wasabi, Zata, Other
...

Storage> 4
```
</details>

<details markdown='1'>
<summary markdown='span'>
Provider configuration in Rclone
</summary>
```text
Option provider.
Choose your S3 provider.
Choose a number from below, or type in your own value.
Press Enter to leave empty.
 1 / Amazon Web Services (AWS) S3
   \ (AWS)
 2 / Alibaba Cloud Object Storage System (OSS) formerly Aliyun
   \ (Alibaba)
 3 / Arvan Cloud Object Storage (AOS)
   \ (ArvanCloud)
 4 / Bizfly Cloud Simple Storage
   \ (BizflyCloud)
 5 / Ceph Object Storage
   \ (Ceph)
 6 / China Mobile Ecloud Elastic Object Storage (EOS)
   \ (ChinaMobile)
 7 / Cloudflare R2 Storage
   \ (Cloudflare)
...

provider> 7
```
</details>

To upload your data to the R2 bucket, run:

```sql
-- TODO: simplify
rclone cp -v ⟨your_ducklake_catalog.ducklake⟩ ⟨your_rclone_remote⟩:⟨your_bucket_name⟩/⟨path⟩/
rclone sync -v ⟨your_ducklake_directory⟩ ⟨your_rclone_remote⟩:⟨your_bucket_name⟩/⟨path⟩/
```

### Setting the CORS Policy (Optional)

If you try to query the dataset from another website – such as the [online DuckDB shell](https://shell.duckdb.org/) –, you will get an error due to CORS (Cross-Origin Resource Sharing) security mechanism. To allow querying the dataset, add a CORS policy to the Cloudflare configuration of the bucket. Assuming that you want to access the datasets using `shell.duckdb.org`, you can use the following configuration:

```json
...
```

## Pricing

The following is an overview of the costs involved with storing a DuckLake on Cloudflare R2.
As of February 2026, Cloudflare R2's pricing has the following components:

* Storage: $0.015/GB/month
* Class A operations: 1 million requests/month free, $4.50/million requests above
* Class B operations: 10 million requests/month free, $0.36/million requests above
* Egressing data: free

Serving a read-only DuckLake requires primarily Class B operations, so it should stay in the free tier even with thousands of users querying every month. For more details, please consult [Cloudflare R2's “Pricing” page](https://developers.cloudflare.com/r2/pricing/).
