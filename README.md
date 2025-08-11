# AI Strategy Assistant - Main Application


https://github.com/user-attachments/assets/08bc5e7d-6e42-4016-af1e-62c3147b900d





A business-first development tool that validates your project idea before you write any code. This Streamlit application provides an interactive interface for the complete business analysis workflow.

## Features

### 🎯 Business Validation

- Interactive form for project description and target customer input
- Automated business viability scoring (1-10 scale)
- Validation gates that prevent development of unviable projects

### 🔍 Market Research

- Automated web research using Crawl4AI
- Competitive analysis and market trend identification
- Research data integration into business planning

### 🛠️ MVP Planning

- Feature specification generation with user stories
- Impact vs Effort matrix visualization using Plotly
- Priority-based feature organization (Core, Important, Future)

### 🚀 Go-to-Market Strategy

- Distribution channel identification
- Pricing strategy development
- Launch timeline with milestones
- Success metrics definition

### 💾 Session Management

- Persistent state management across sessions
- Session save/load functionality
- Backward compatibility for data model changes

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set API Key

```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 3. Run Application

```bash
# Using the startup script (recommended)
python run_app.py

# Or directly with Streamlit
streamlit run app.py
```

### 4. Access Application

Open your browser to `http://localhost:8501`

## Usage Guide

### Configuration

1. **API Key**: Enter your OpenAI API key in the sidebar or set the `OPENAI_API_KEY` environment variable
2. **Model Selection**: Choose your preferred language model (GPT-4, GPT-3.5, Claude, etc.)
3. **System Status**: Verify all components are initialized correctly

### Business Analysis Workflow

1. **Describe Your Project**: Enter a detailed description of your project idea
2. **Target Customer**: Specify your target customer segment
3. **Additional Context**: Optionally provide market size, existing solutions, and unique advantages
4. **Submit for Analysis**: Click "Validate Business Opportunity" to start the workflow

### Results Review

- **Validation Score**: Review the business viability score (must be ≥7 to proceed)
- **Business Model**: Examine the generated value proposition and revenue streams
- **Feature Matrix**: Use the impact/effort visualization to prioritize features
- **GTM Strategy**: Review distribution channels, pricing, and launch timeline
- **Product Roadmap**: Follow the 3-phase development plan

### Session Management

- **Save Session**: Preserve your analysis for future reference
- **Load Session**: Resume previous analysis sessions
- **Clear Session**: Start fresh with a new project

## Application Architecture

### Core Components

- **`app.py`**: Main Streamlit application with workflow orchestration
- **`orchestrator.py`**: LangGraph-based multi-agent workflow engine
- **`ui/product_strategy_ui.py`**: Reusable UI components and visualizations
- **`memory/graph_memory.py`**: Persistent session state management

### Data Flow

1. User input → Business validation form
2. Form submission → Workflow execution
3. Multi-agent analysis → State updates
4. Results generation → UI display
5. Session persistence → Memory storage

## Configuration Options

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `DEBUG`: Set to "true" for detailed error information
- `STREAMLIT_SERVER_PORT`: Custom port (default: 8501)

### Model Options

- `openai/gpt-4o-mini` (default, cost-effective)
- `openai/gpt-4o` (most capable)
- `openai/gpt-3.5-turbo` (fast and affordable)
- `anthropic/claude-3-haiku` (alternative provider)
- `anthropic/claude-3-sonnet` (high-quality alternative)

## Troubleshooting

### Common Issues

**"API Key required" warning**

- Set your OpenAI API key in the sidebar or environment variable
- Verify the key is valid and has sufficient credits

**"System not initialized" error**

- Check that all dependencies are installed correctly
- Verify the API key is configured properly
- Review the system status in the sidebar

**Workflow execution fails**

- Check your internet connection for web research
- Verify API key has sufficient credits
- Review error messages in the application

**Session loading fails**

- Check if the session file exists and is readable
- Try clearing the session and starting fresh
- Review memory statistics in the sidebar

### Performance Tips

- Use GPT-4o-mini for faster, cost-effective analysis
- Save sessions regularly to preserve work
- Clear old sessions periodically to reduce memory usage

## Development

### Running in Development Mode

```bash
export DEBUG=true
streamlit run app.py --server.runOnSave true
```

### Testing the Application

```bash
# Test syntax
python -m py_compile app.py

# Test dependencies
python run_app.py --check-only
```

## Requirements Compliance

This application implements the following requirements:

- **6.1**: Business validation section with problem statement input and target customer fields
- **6.4**: GTM strategy display with metrics, channels, and pricing in structured layout
- **8.1**: Unique session ID creation and ProductState initialization
- **8.3**: Complete state restoration including business model, features, and research data

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review the application logs for detailed error information
3. Verify all dependencies are correctly installed
4. Ensure your API key is valid and has sufficient credits
