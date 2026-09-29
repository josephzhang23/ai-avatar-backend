import argparse, json, os

from database.connection import get_session

from dreambooth.utils import get_weights_dir, get_instance_dir, get_class_data_dir

from models.models import Instance

parser = argparse.ArgumentParser()
parser.add_argument(
    "--instance_id",
    type=int,
    required=True,
)
args = parser.parse_args()

session = next(get_session())
instance = session.get(Instance, args.instance_id)
output_dir = get_weights_dir(instance)
os.makedirs(output_dir, exist_ok=True)
instance_dir = get_instance_dir(instance.uuid)

concepts_list = [
    {
        "instance_prompt":      f"photo of sks {instance.class_name}",
        "class_prompt":         f"photo of a {instance.class_name}",
        "instance_data_dir":    instance_dir,
        "class_data_dir":       get_class_data_dir(instance)
    },
]

for c in concepts_list:
    os.makedirs(c["instance_data_dir"], exist_ok=True)

with open("concepts_list.json", "w") as f:
    json.dump(concepts_list, f, indent=4)

os.system(f'''
accelerate launch train_dreambooth.py \
--pretrained_model_name_or_path=runwayml/stable-diffusion-v1-5 \
--pretrained_vae_name_or_path="stabilityai/sd-vae-ft-mse" \
--output_dir={output_dir} \
--revision="fp16" \
--with_prior_preservation --prior_loss_weight=1.0 \
--seed=1337 \
--resolution=512 \
--train_batch_size=1 \
--train_text_encoder \
--mixed_precision="fp16" \
--use_8bit_adam \
--gradient_accumulation_steps=1 \
--learning_rate=1e-6 \
--lr_scheduler="constant" \
--lr_warmup_steps=0 \
--num_class_images=50 \
--sample_batch_size=4 \
--max_train_steps={len(os.listdir(instance_dir)) * 100} \
--save_interval=10000 \
--save_sample_prompt="photo of sks {instance.class_name}" \
--concepts_list="concepts_list.json"
''')