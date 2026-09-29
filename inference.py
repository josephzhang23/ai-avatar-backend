import argparse, uuid, os, sys, torch, math
from torch import autocast
from diffusers import StableDiffusionPipeline, DDIMScheduler, EulerAncestralDiscreteScheduler

# from database.connection import get_session
# from models.models import Instance, Task, Avatar

# from dreambooth.utils import get_outputs_dir

parser = argparse.ArgumentParser()
# parser.add_argument(
#     "--instance_id",
#     type=int,
#     required=True,
# )
# parser.add_argument(
#     "--task_id",
#     type=int,
#     required=True,
# )
# parser.add_argument(
#     "--style_id",
#     type=int,
#     required=True,
# )
parser.add_argument(
    "--model_path",
    type=str
)
parser.add_argument(
    "--prompt",
    type=str
)
parser.add_argument(
    "--width",
    type=int,
    default=512,
)
parser.add_argument(
    "--height",
    type=int,
    default=512,
)
parser.add_argument(
    "--guidance_scale",
    type=float,
    default=7,
)
parser.add_argument(
    "--num_images",
    type=int,
    default=8
)
parser.add_argument(
    "--num_images_per_prompt",
    type=int,
    default=4
)
parser.add_argument(
    "--num_inference_steps",
    type=int,
    default=50,
)
parser.add_argument(
    "--strength",
    type=float,
    default=None,
)
parser.add_argument(
    "--negative_prompt",
    type=str,
    default="",
)
parser.add_argument(
    "--output_path",
    type=str
)
args = parser.parse_args()

# session = next(get_session())
# instance = session.get(Instance, args.instance_id)
# task = session.get(Task, args.task_id)
# output_path = get_outputs_dir(instance)
num_images_per_prompt = args.num_images_per_prompt

scheduler = EulerAncestralDiscreteScheduler(beta_start=0.00085, beta_end=0.012, beta_schedule="scaled_linear")
pipe = StableDiffusionPipeline.from_pretrained(args.model_path, scheduler=scheduler, safety_checker=None, torch_dtype=torch.float16).to("cuda")
g_cuda = None
g_cuda = torch.Generator(device='cuda')
g_cuda.seed()
with autocast("cuda"), torch.inference_mode():
    for i in range(math.ceil(args.num_images / num_images_per_prompt)):
        images = pipe(
            args.prompt,
            height=args.height,
            width=args.width,
            negative_prompt=args.negative_prompt,
            num_images_per_prompt=num_images_per_prompt,
            num_inference_steps=args.num_inference_steps,
            # strength=args.strength,
            guidance_scale=args.guidance_scale,
            generator=g_cuda
        ).images
        for image in images:
            filename = f"{uuid.uuid4()}.png"
            image.save(f"{args.output_path}/{filename}")
            # avatar = Avatar(instance_id=instance.id, style_id=args.style_id, task_id=task.id, filename=filename)
            # session.add(avatar)
    # session.commit()