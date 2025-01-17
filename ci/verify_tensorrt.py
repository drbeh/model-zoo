# Copyright (c) MONAI Consortium
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

import torch
from bundle_custom_data import include_verify_tensorrt_list
from monai.bundle import trt_export
from verify_bundle import _find_bundle_file


def verify_tensorrt(bundle_path: str, net_id: str, config_file: str, precision: str):
    """
    This function is used to verify if the checkpoint is able to export into TensorRT model, and
    the exported model will be checked if it is able to be loaded successfully.

    """
    trt_model_path = os.path.join(bundle_path, f"models/model_trt_{precision}.ts")
    try:
        trt_export(
            net_id=net_id,
            filepath=trt_model_path,
            ckpt_file=os.path.join(bundle_path, "models/models.pt"),
            meta_file=os.path.join(bundle_path, "configs/metadata.json"),
            config_file=os.path.join(bundle_path, config_file),
            precision=precision,
            bundle_root=bundle_path,
        )
    except Exception as e:
        print(f"'trt_export' failed with error: {e}")
        raise
    try:
        torch.jit.load(trt_model_path)
    except Exception as e:
        print(f"load TensorRT model {trt_model_path} failed with error: {e}")
        raise


def verify_all_tensorrt_bundles(models_path="models"):
    """
    This function is used to verify all bundles that support TensorRT.

    """
    for bundle in include_verify_tensorrt_list:
        print(f"start verifying bundle {bundle}.")
        bundle_path = os.path.join(models_path, bundle)
        net_id, inference_file_name = "network_def", _find_bundle_file(
            os.path.join(bundle_path, "configs"), "inference"
        )
        config_file = os.path.join("configs", inference_file_name)
        for precision in ["fp32", "fp16"]:
            try:
                verify_tensorrt(bundle_path=bundle_path, net_id=net_id, config_file=config_file, precision=precision)
                print(f"export bundle {bundle} weights into TensorRT module with precision {precision} successfully.")
            except BaseException:
                print(f"verify bundle {bundle} with precision {precision} failed.")
                raise


if __name__ == "__main__":
    verify_all_tensorrt_bundles()
