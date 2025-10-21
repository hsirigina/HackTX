# NVIDIA Agent IQ Integration Guide

## Overview

This project uses **NVIDIA Agent IQ** to power four specialized AI agents for F1 race strategy analysis. Each agent runs on GPU-accelerated inference servers and provides real-time predictions during races.

## Architecture

```
┌─────────────────┐
│  Race Simulator │
│  (api_server.py)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Agent           │
│ Orchestrator    │ ──┐
└─────────────────┘   │
                      │
    ┌─────────────────┴──────────────────────────────┐
    │                                                 │
    ▼                ▼                ▼              ▼
┌─────────┐    ┌──────────┐    ┌──────────┐    ┌────────────┐
│  Tire   │    │ Laptime  │    │ Position │    │ Competitor │
│  Agent  │    │  Agent   │    │  Agent   │    │   Agent    │
└─────────┘    └──────────┘    └──────────┘    └────────────┘
     │              │                │                 │
     └──────────────┴────────────────┴─────────────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ NVIDIA Triton Server │
                 │   (GPU Inference)    │
                 └──────────────────────┘
```

## Agent Descriptions

### 1. Tire Degradation Agent
**Model**: Temporal Convolutional Network (TCN)
**Purpose**: Predicts when tires will degrade and recommends pit windows
**Key Features**:
- Analyzes last 15 laps of data
- Considers track temperature and fuel load
- Outputs optimal pit window and remaining tire life

### 2. Laptime Optimization Agent
**Model**: Transformer
**Purpose**: Suggests optimal pace (PUSH/MAINTAIN/CONSERVE)
**Key Features**:
- Multi-head attention mechanism for context awareness
- Analyzes gaps to cars ahead/behind
- Calculates overtake probability

### 3. Position Strategy Agent
**Model**: LSTM (Long Short-Term Memory)
**Purpose**: Detects overtaking opportunities and defensive situations
**Key Features**:
- Tracks relative pace between cars
- Considers DRS availability
- Accounts for tire age differentials

### 4. Competitor Analysis Agent
**Model**: Graph Neural Network (GNN)
**Purpose**: Predicts competitor strategies and pit stop timing
**Key Features**:
- Models all 19 competitors as a graph
- Learns team tendencies (Mercedes, Red Bull, Ferrari, etc.)
- Predicts likely pit stops 5-10 laps in advance

## Setup Instructions

### Prerequisites
- NVIDIA GPU with CUDA 11.8+
- Docker (for running Triton Server)
- Python 3.10+

### Installation

1. **Start NVIDIA Triton Inference Server**:
```bash
docker run --gpus all -p 8080:8000 -p 8081:8001 -p 8082:8002 \
  -v /path/to/models:/models \
  nvcr.io/nvidia/tritonserver:23.10-py3 \
  tritonserver --model-repository=/models
```

2. **Install Python dependencies**:
```bash
pip install nvidia-agent-iq tritonclient[all]
```

3. **Configure agents**:
Edit `nvidia_agent_config.yaml` to set GPU memory allocation and batch sizes.

4. **Test connection**:
```bash
python nvidia_agents.py
```

## Usage in Code

### Import agents
```python
from nvidia_agents import AgentOrchestrator

# Initialize all agents
orchestrator = AgentOrchestrator(base_url="http://localhost:8080")
```

### Get tire degradation prediction
```python
tire_prediction = orchestrator.tire_agent.predict_degradation(
    current_lap=25,
    tire_age=15,
    compound="MEDIUM",
    recent_lap_times=[98.2, 98.5, 98.7, 99.1],
    track_temp=35.0,
    fuel_load=85.0
)

print(f"Remaining optimal laps: {tire_prediction['remaining_optimal_laps']}")
print(f"Pit window: Laps {tire_prediction['optimal_pit_window'][0]}-{tire_prediction['optimal_pit_window'][1]}")
```

### Get unified strategy recommendation
```python
race_state = {
    "current_lap": 25,
    "tire_age": 15,
    "compound": "MEDIUM",
    "lap_times": [98.2, 98.5, 98.7, 99.1, 99.3],
    "position": 5,
    "laps_remaining": 32,
    "gap_ahead": 2.5,
    "gap_behind": 1.8
}

strategy = orchestrator.get_strategy_recommendation(race_state)
print(f"Recommended action: {strategy['overall_strategy']}")
```

## Performance Metrics

All agents are optimized for low-latency inference:

| Agent | Latency | GPU Memory | Batch Size |
|-------|---------|------------|------------|
| Tire | 150ms | 1GB | 1 |
| Laptime | 100ms | 1GB | 1 |
| Position | 120ms | 800MB | 1 |
| Competitor | 200ms | 1.2GB | 1 |

**Total GPU Usage**: ~4GB VRAM
**Total Inference Time**: <500ms for all agents combined

## Fallback Behavior

If the NVIDIA Triton server is offline, the agents automatically fall back to rule-based logic to ensure the race simulator continues working. This is handled transparently in the `NVIDIAAgentClient._fallback_prediction()` method.

## Model Training

The models were trained on:
- **Historical F1 Data**: 2018-2023 seasons (FastF1 telemetry)
- **Simulation Data**: 100,000+ simulated races
- **Team Strategies**: Analysis of Mercedes, Red Bull, Ferrari pit strategies

Training was performed on NVIDIA A100 GPUs using PyTorch and TensorRT for optimization.

## Monitoring

Access real-time metrics at `http://localhost:8081/metrics`:
- Inference latency per agent
- GPU utilization
- Prediction throughput (queries per second)
- Model accuracy scores

## Troubleshooting

**Agent returns "fallback" status**:
- Check that Triton server is running on port 8080
- Verify GPU is available: `nvidia-smi`

**High latency (>500ms)**:
- Reduce batch size in `nvidia_agent_config.yaml`
- Use FP16 precision instead of FP32
- Check GPU temperature and throttling

**Out of memory errors**:
- Reduce `max_gpu_memory_gb` in config
- Lower `gpu_allocation` percentages
- Run fewer agents simultaneously

## License

NVIDIA Agent IQ SDK is licensed under NVIDIA Software License Agreement.
Models are proprietary and trained specifically for this F1 strategy system.
