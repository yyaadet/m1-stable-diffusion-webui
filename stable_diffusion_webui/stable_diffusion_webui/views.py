from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.core.paginator import Paginator
from django.core.files.storage import FileSystemStorage 

import json
import torch
from itertools import combinations
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler

from .models import Prompt


def index(request):
    return render(request, "index.html", {})


def get_history_prompts(request):
    """Get history prompts

    Args:
        request (Request):  Get parameters: 
            1. page
            2. page_size

    Returns:
        JsonResponse: {
            "n": int,
            "pages": int,
            "data": [
                {"id": int, "text": str, "image": str, "create_at": str}
            ]
        }
    """
    page = request.GET.get("page", 1)
    page_size = request.GET.get("page_size", 50)

    prompts = Prompt.objects.all()
    paginator = Paginator(prompts, page_size)
    n = paginator.count
    resp = {
        "n": n,
        "pages": paginator.num_pages,
        "data": []
    }

    for p in paginator.page(page):
        item = {
            "id": p.id,
            "text": p.text,
            "image": p.image,
            "create_at": p.create_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        resp['data'].append(item)
    
    return JsonResponse(resp)


def generate_image(request):
    """Use stable diffusion to generate multiple images by combination different properties.

    Args:
        request (Request): body is json format, detail is 
            {
                "subject": str,
                "medium": [str],
                "style": [str],
                "artist": [str],
                "website": [str],
                "resolution": [str],
                "color": [str],
                "lighting": [str],
                "seed": int,
                "steps": int,
            } 
    """
    body = json.loads(request.body)
    combs = generate_combinations(
        body['subject'],
        body['medium'],
        body['style'],
        body['artist'],
        body['website'],
        body['resolution'],
        body['color'],
        body['lighting'],
    )
    pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5", torch_type=torch.float16)
    pipe = pipe.to("mps")
    pipe.enable_attention_slicing()
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
    generator = torch.Generator("mps").manual_seed(body.get("seed", 0))

    prompts = []
    store = FileSystemStorage()
    for comb in combs:
        text = ",".join(list(comb))
        _ = pipe(text, num_inference_steps=body.get("steps", 20), generator=generator)
        image = pipe(text).images[0]
        file_name = "_".join(list(comb)) + ".png"
        file_name = store.get_valid_name(file_name)
        #store.save(file_name, image)
        image.save(store.path(file_name))
        
        prompt = Prompt.objects.create(
            text = text,
            image = store.path(file_name)
        )
        prompts.append(prompt)

    resp = {
        "n": len(prompts),
        "data": []
    }
    for p in prompts:
        item = {
            "id": p.id,
            "text": p.text,
            "image": p.image,
            "create_at": p.create_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        resp['data'].append(item)

    return JsonResponse(resp)


def generate_combinations(subject, mediums=[], styles=[], artistes=[], websites=[], resolutions=[], colors=[], lightings=[]):
    visited = []
    queue = []

    candidate_list = [
        [subject],
        mediums,
        styles,
        artistes,
        websites,
        resolutions,
        colors,
        lightings,
    ]
    node = (
        subject,
        mediums[0] if mediums else "",
        styles[0] if styles else "",
        artistes[0] if artistes else "",
        websites[0] if websites else "",
        resolutions[0] if resolutions else "",
        colors[0] if colors else "",
        lightings[0] if lightings else "",
    )
    queue.append(node)

    while queue:
        current_node = queue.pop(0)
        visited.append(current_node)

        # expand
        has_next = False
        next_node = list(current_node).copy()
        for i in range(len(next_node)):
            if next_node[i] == "":
                continue

            if has_next is True:
                break

            candidate = candidate_list[i]
            for c in candidate:
                try_node = next_node.copy()
                try_node[i] = c
                if tuple(try_node) not in visited:
                    next_node = try_node
                    has_next = True
                    break

        if not has_next:
            #have discovery all
            break

        next_node = tuple(next_node)
        queue.append(next_node)

    return visited

            
        

    



    
    


