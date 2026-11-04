# bbe-ai

![Version: 0.0.1](https://img.shields.io/badge/Version-0.0.1-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square)

A voice assistant's speech and language models for Home Assistant, run on the BBE cluster's CPUs, with speech-to-text and text-to-speech over Wyoming and a small LLM in Ollama

**Homepage:** <https://brains-beyond-expectations.github.io/bbe-charts>

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| bbe.ai.allowFrom | list | `[]` | More addresses let in, as CIDRs, such as `192.168.1.20/32` for a computer to try the models from |
| bbe.ai.dataSize | string | `"15Gi"` | The size of the volume holding the downloaded models. Parakeet is ~0.7Gi, a Piper voice ~0.1Gi and a 4B model ~2.5Gi, and downloads keep a cache of their own next to them |
| bbe.ai.homeAssistantIP | string | `""` | The IP address of the machine running Home Assistant, the only one let in |
| bbe.ai.loadBalancerIP | string | `""` | A free IP address on your LAN for Home Assistant to reach the models at, outside your router's DHCP range, which MetalLB announces. Speech-to-text is on port 10300, text-to-speech on 10200 and Ollama on 11434 |
| bbe.ai.ollama.contextLength | int | `8192` | The context it's loaded with, in tokens, unless a request asks for another. Home Assistant asks for its own "Context window size", 8192 by default, and the memory below has to hold it |
| bbe.ai.ollama.enabled | bool | `true` | Whether to run an LLM for Home Assistant to talk to. Off, Home Assistant's own conversation agent handles what's said, and the speech runs on any node |
| bbe.ai.ollama.image.repository | string | `"ollama/ollama"` | Ollama, which runs the LLM and serves it to Home Assistant's Ollama integration |
| bbe.ai.ollama.image.tag | string | `"0.40.14"` | Ollama's version |
| bbe.ai.ollama.kvCacheType | string | `"q8_0"` | How the context is stored: `q8_0` takes half the memory of `f16`, with flash attention |
| bbe.ai.ollama.model | string | `"qwen3:1.7b"` | The model it downloads, from https://ollama.com/library, which it needs to call Home Assistant's tools. `qwen3:1.7b` fits an 8 GB node. `qwen3:4b-instruct`, Home Assistant's default, answers better and needs 4Gi |
| bbe.ai.ollama.resources.limits.memory | string | `"2560Mi"` | The memory to limit Ollama to, the same as requested, so it never takes memory the node's other apps rely on |
| bbe.ai.ollama.resources.requests.cpu | string | `"500m"` | The CPU to request for Ollama. It uses every core while it answers |
| bbe.ai.ollama.resources.requests.memory | string | `"2560Mi"` | The memory to request for Ollama. The model and its context have to fit, so the pod only runs on a node with that much to spare |
| bbe.ai.speechToText.image.repository | string | `"rhasspy/wyoming-whisper"` | The Wyoming speech-to-text server, with faster-whisper, NVIDIA's Parakeet and other backends |
| bbe.ai.speechToText.image.tag | string | `"3.8.1"` | The server's version |
| bbe.ai.speechToText.language | string | `"en"` | The language spoken to it. Home Assistant's pipeline is offered only the languages the model transcribes |
| bbe.ai.speechToText.library | string | `"auto"` | The backend: `auto` picks one per language, which is Parakeet through sherpa-onnx for English. `faster-whisper` with the model `base.en` is lighter, and can be biased toward Home Assistant's names |
| bbe.ai.speechToText.model | string | `"auto"` | The model: `auto` picks the backend's default, which is `sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8` for English |
| bbe.ai.speechToText.resources.limits.memory | string | `"2Gi"` | The memory to limit speech-to-text to |
| bbe.ai.speechToText.resources.requests.cpu | string | `"100m"` | The CPU to request for speech-to-text |
| bbe.ai.speechToText.resources.requests.memory | string | `"1Gi"` | The memory to request for speech-to-text |
| bbe.ai.textToSpeech.image.repository | string | `"rhasspy/wyoming-piper"` | The Wyoming text-to-speech server, with Piper |
| bbe.ai.textToSpeech.image.tag | string | `"2.5.2"` | The server's version |
| bbe.ai.textToSpeech.resources.limits.memory | string | `"512Mi"` | The memory to limit text-to-speech to |
| bbe.ai.textToSpeech.resources.requests.cpu | string | `"50m"` | The CPU to request for text-to-speech |
| bbe.ai.textToSpeech.resources.requests.memory | string | `"128Mi"` | The memory to request for text-to-speech |
| bbe.ai.textToSpeech.voice | string | `"en_US-lessac-medium"` | The voice it speaks with by default. Home Assistant can pick another per pipeline, which is downloaded the first time it's used. See https://rhasspy.github.io/piper-samples |
| bbe.networkPolicy.enabled | bool | `true` | Whether only Home Assistant, and `bbe.ai.allowFrom`, may reach the models. Wyoming and Ollama have no sign-in, so anything that reaches them can use them. The cluster's network has to enforce NetworkPolicies, which `bbe setup` turns on for the clusters it creates |

