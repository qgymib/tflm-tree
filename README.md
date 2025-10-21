# tflm-tree

Third-party porting for [TensorFlow Lite for Microcontrollers](https://github.com/tensorflow/tflite-micro).

## Upstream version

commit: [cee9550a3770b0c6bb560276db86f6b21895f597](https://github.com/tensorflow/tflite-micro/commit/cee9550a3770b0c6bb560276db86f6b21895f597)

## Sync with upstream.

Note: The following tools must installed:

```
wget unzip
```

1. Create a python virtual environment:
    ```bash
    python3 -m venv .venv
    ```

2. Activate the virtual environment:
    ```bash
    source .venv/bin/activate
    ```

3. run script to sync:
    ```bash
    python3 tools/sync_with_upstream_tflite.py
    ```
