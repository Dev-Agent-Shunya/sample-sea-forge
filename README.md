# SeaForge 🌊

**Agent Zero Orchestrated Development Platform**

SeaForge is an autonomous code generation platform that uses Agent Zero as the orchestrator with GitHub-based storage instead of local files.

## Features

- 🤖 **Agent Zero Orchestration** - Intelligent task delegation and monitoring
- 🌐 **GitHub Storage** - All iterations stored as branches with cherry-pick inheritance
- 📊 **Real-time Dashboard** - Live monitoring of feature progress
- 🔄 **Cherry-pick Workflow** - Seamless iteration inheritance

## Workflow

### Phase 1: Planning (000-099)
- No pull requests
- Cherry-pick from previous planning iterations
- Branch format: `SFG00-000-<DD/MM/YY>`

### Phase 2: Development (100-999)
- Pull requests to main
- Cherry-pick from last planning or development branch
- Branch format: `SFG00-100-<DD/MM/YY>`

## Usage

```bash
python seaforge/server.py
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER                                  │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              AGENT ZERO (Orchestrator)                     │
│  • Planning with user                                      │
│  • Delegate to subordinates                                │
│  • Monitor via dashboard                                   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      SUBORDINATES                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Planning   │  │   Developer  │  │    Git       │      │
│  │    Agent     │  │    Agent     │  │   Manager    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     GITHUB REPO                            │
│  • Branches per iteration                                  │
│  • Cherry-pick inheritance                                 │
│  • Pull requests (dev only)                                │
└─────────────────────────────────────────────────────────────┘
```
