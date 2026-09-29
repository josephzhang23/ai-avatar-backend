import argparse, uuid, os, torch, math, subprocess
from sqlmodel import Session
from torch import autocast
from diffusers import StableDiffusionPipeline, EulerAncestralDiscreteScheduler

from database.connection import get_session
from models.models import Instance, Task, Avatar

from dreambooth.utils import get_weights_dir, get_outputs_dir, OUTPUT_DIR

parser = argparse.ArgumentParser()
parser.add_argument(
    "--instance_id",
    type=int,
    required=True,
)
parser.add_argument(
    "--task_id",
    type=int,
    required=True,
)
args = parser.parse_args()

session = next(get_session())
instance = session.get(Instance, args.instance_id)
task = session.get(Task, args.task_id)
weights_path = get_weights_dir(instance)

if os.listdir(weights_path):
    model_path = f"{weights_path}/{max(fname for fname in os.listdir(weights_path))}" 
    output_path = get_outputs_dir(instance)
    os.system(f'mkdir -p {output_path}')
    scheduler = EulerAncestralDiscreteScheduler(beta_start=0.00085, beta_end=0.012, beta_schedule="scaled_linear")
    pipe = StableDiffusionPipeline.from_pretrained(model_path, scheduler=scheduler, safety_checker=None, torch_dtype=torch.float16).to("cuda")
    task_style_links = task.task_style_links
    # print(f"styles: {styles}")
    g_cuda = None
    g_cuda = torch.Generator(device='cuda')
    g_cuda.seed()
    with autocast("cuda"), torch.inference_mode():
        num_images_per_prompt = 1
        for task_style_link in task_style_links:
            style = task_style_link.style
            prompt = style.prompt.format(CLASS_NAME = instance.class_name)
            print("prompt: " + prompt)
            for i in range(math.ceil(task_style_link.num_images / num_images_per_prompt)):
                images = pipe(
                    prompt,
                    height=style.height,
                    width=style.width,
                    # negative_prompt=negative_prompt,
                    num_images_per_prompt=num_images_per_prompt,
                    num_inference_steps=50,
                    # strength=args.strength,
                    guidance_scale=style.guidance_scale or 7,
                    generator=g_cuda
                ).images
                for image in images:
                    filename = f"{uuid.uuid4()}.png"
                    image.save(f"{output_path}/{filename}")
                    avatar = Avatar(instance_id=instance.id, style_id=style.id, task_id=task.id, filename=filename)
                    session.add(avatar)
        command = f"rsync -rt {output_path} main:{OUTPUT_DIR}/ && rm -r {output_path}"
        subprocess.run(command, shell=True)
        session.commit()