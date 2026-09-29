# AI Avatar Backend

Python backend for **AI Avatar – Your Face by AI**, an iOS app that turned a
handful of selfies into stylized AI portraits. Written in early 2023 and no
longer maintained; published as a reference.

## How it worked

1. The app uploads 10–20 photos of a person (an *instance*).
2. A DreamBooth fine-tune of Stable Diffusion 1.5 is trained on those photos.
3. The fine-tuned model renders the person in a set of preset styles/packs.
4. The app polls task status and downloads the generated avatars.

## Layout

| Path | Purpose |
| --- | --- |
| `main.py` | FastAPI app: `/style`, `/instance`, `/avatar`, `/task` routes |
| `routes/` | API route handlers |
| `models/` | SQLModel tables (classes, styles, packs, examples, servers, …) |
| `database/connection.py` | Postgres engine (reads `DATABASE_URL`) |
| `dreambooth/`, `dreambooth_main.py` | Training / generation worker service |
| `train.py`, `train_dreambooth.py` | DreamBooth training entry points |
| `inference.py`, `generate_images.py` | Image generation |
| `convert_diffusers_to_original_stable_diffusion.py` | Diffusers → `.ckpt` conversion |

## Running

```bash
pip install -r requirements.txt
export DATABASE_URL="postgresql://user:password@host/dbname"
uvicorn main:app --host 0.0.0.0 --port 8000
```

Training and inference need a CUDA GPU and the Stable Diffusion 1.5 weights,
which are not included. Image URLs in `routes/` point at the original
production host and will need to be changed.

## License

MIT — see [LICENSE](LICENSE). Two training/conversion scripts are third-party
code under the Apache License 2.0; see [NOTICE](NOTICE).
