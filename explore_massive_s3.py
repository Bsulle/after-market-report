#!/usr/bin/env python3
"""
Massive.com S3 Explorer
Run this script to discover what data is available in your Massive.com account.
"""

import sys

try:
    import boto3
    from botocore.config import Config
except ImportError:
    print("boto3 not installed. Run: pip install boto3")
    sys.exit(1)

# Massive.com S3 Configuration
MASSIVE_S3_ENDPOINT = "https://files.massive.com"
MASSIVE_ACCESS_KEY = "03ca9a2a-b150-4ad7-bc6c-491054d89e1d"
MASSIVE_SECRET_KEY = "wm2_rIkTQVxi_xAYrv307R24TvF2Fz7R"
MASSIVE_BUCKET = "flatfiles"


def get_s3_client():
    """Create S3 client for Massive.com."""
    return boto3.client(
        's3',
        endpoint_url=MASSIVE_S3_ENDPOINT,
        aws_access_key_id=MASSIVE_ACCESS_KEY,
        aws_secret_access_key=MASSIVE_SECRET_KEY,
        config=Config(signature_version='s3v4')
    )


def list_all_prefixes(prefix='', delimiter='/'):
    """List all 'folders' (common prefixes) at a given level."""
    s3 = get_s3_client()

    try:
        response = s3.list_objects_v2(
            Bucket=MASSIVE_BUCKET,
            Prefix=prefix,
            Delimiter=delimiter,
            MaxKeys=1000
        )

        prefixes = []
        if 'CommonPrefixes' in response:
            for p in response['CommonPrefixes']:
                prefixes.append(p['Prefix'])

        files = []
        if 'Contents' in response:
            for obj in response['Contents']:
                if obj['Key'] != prefix:  # Skip the prefix itself
                    files.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'modified': obj['LastModified'].strftime('%Y-%m-%d %H:%M')
                    })

        return prefixes, files

    except Exception as e:
        print(f"Error: {str(e)}")
        return [], []


def explore_bucket():
    """Interactive exploration of the S3 bucket."""
    print("=" * 70)
    print("Massive.com S3 Data Explorer")
    print("=" * 70)
    print(f"\nEndpoint: {MASSIVE_S3_ENDPOINT}")
    print(f"Bucket: {MASSIVE_BUCKET}")
    print()

    current_prefix = ''

    while True:
        print(f"\nCurrent path: /{current_prefix}")
        print("-" * 50)

        prefixes, files = list_all_prefixes(current_prefix)

        # Show folders
        if prefixes:
            print("\nFolders:")
            for i, p in enumerate(prefixes):
                folder_name = p.replace(current_prefix, '').rstrip('/')
                print(f"  [{i}] {folder_name}/")

        # Show files (limit to first 20)
        if files:
            print(f"\nFiles ({len(files)} total):")
            for f in files[:20]:
                size_kb = f['size'] / 1024
                print(f"  - {f['key'].replace(current_prefix, '')} ({size_kb:.1f} KB, {f['modified']})")
            if len(files) > 20:
                print(f"  ... and {len(files) - 20} more files")

        if not prefixes and not files:
            print("\n(empty or no access)")

        # Navigation options
        print("\nOptions:")
        print("  [number] - Enter folder")
        print("  [b] - Go back")
        print("  [r] - Return to root")
        print("  [d] - Download sample file")
        print("  [q] - Quit")

        choice = input("\nChoice: ").strip().lower()

        if choice == 'q':
            break
        elif choice == 'b':
            # Go back one level
            parts = current_prefix.rstrip('/').split('/')
            if parts and parts[0]:
                current_prefix = '/'.join(parts[:-1])
                if current_prefix:
                    current_prefix += '/'
            else:
                current_prefix = ''
        elif choice == 'r':
            current_prefix = ''
        elif choice == 'd' and files:
            # Download first file as sample
            sample_file = files[0]['key']
            print(f"\nDownloading sample: {sample_file}")
            try:
                s3 = get_s3_client()
                response = s3.get_object(Bucket=MASSIVE_BUCKET, Key=sample_file)
                content = response['Body'].read()

                # Try to decode as text
                try:
                    text = content.decode('utf-8')
                    print("\nFile contents (first 2000 chars):")
                    print("-" * 50)
                    print(text[:2000])
                    if len(text) > 2000:
                        print(f"\n... ({len(text) - 2000} more characters)")
                except:
                    print(f"\nBinary file ({len(content)} bytes)")

            except Exception as e:
                print(f"Error downloading: {str(e)}")
        elif choice.isdigit():
            idx = int(choice)
            if 0 <= idx < len(prefixes):
                current_prefix = prefixes[idx]
        else:
            print("Invalid choice")


def quick_scan():
    """Quick scan of the bucket structure."""
    print("=" * 70)
    print("Quick Scan of Massive.com S3 Bucket")
    print("=" * 70)

    s3 = get_s3_client()

    # Get root level folders
    prefixes, files = list_all_prefixes('')

    print("\nRoot level folders:")
    for p in prefixes:
        print(f"  - {p}")

    print("\nRoot level files:")
    for f in files[:10]:
        print(f"  - {f['key']} ({f['size']} bytes)")

    # Try to find stock/options data
    print("\n" + "=" * 70)
    print("Searching for stock/options data...")
    print("=" * 70)

    search_prefixes = [
        'stocks/', 'equity/', 'options/', 'daily/', 'eod/',
        'market/', 'data/', 'us/', 'prices/', 'ohlc/'
    ]

    for prefix in search_prefixes:
        sub_prefixes, sub_files = list_all_prefixes(prefix)
        if sub_prefixes or sub_files:
            print(f"\nFound data at '{prefix}':")
            for p in sub_prefixes[:5]:
                print(f"  [folder] {p}")
            for f in sub_files[:5]:
                print(f"  [file] {f['key']} ({f['size']} bytes)")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        quick_scan()
    else:
        print("Run with --quick for a quick scan, or without arguments for interactive mode")
        print()
        explore_bucket()
