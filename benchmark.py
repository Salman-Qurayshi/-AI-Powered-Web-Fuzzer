import subprocess
import json
import os
from collections import defaultdict
from datetime import datetime
from jinja2 import Template
import time

def run_fuzzer(model, run_number, total_runs):
    """Run the fuzzer with a specific model and return discovered links"""
    print(f"\nRunning benchmark for {model} - Run {run_number}/{total_runs}")
    
    # Remove previous all_links.txt if it exists
    if os.path.exists('all_links.txt'):
        os.remove('all_links.txt')
    
    cmd = f'python fuzzer.py "ffuf -w .\\fuzz.txt -u http://127.0.0.1:88/FUZZ -fc 403 -fw 4" --cycles 25 --model {model}'
    try:
        subprocess.run(cmd, shell=True, check=True)
        
        # Read discovered links
        if os.path.exists('all_links.txt'):
            with open('all_links.txt', 'r') as f:
                return set(line.strip() for line in f.readlines())
        return set()
    except subprocess.CalledProcessError as e:
        print(f"Error running fuzzer: {e}")
        return set()

def generate_html_report(results):
    """Generate an HTML report from the benchmark results"""
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Fuzzer Benchmark Results</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .model-section { margin-bottom: 30px; }
            table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .summary { background-color: #e6f3ff; padding: 15px; border-radius: 5px; }
            .timestamp { color: #666; font-size: 0.9em; }
        </style>
    </head>
    <body>
        <h1>Fuzzer Benchmark Results</h1>
        <p class="timestamp">Generated on: {{ timestamp }}</p>
        
        <div class="summary">
            <h2>Summary</h2>
            <p>Total models tested: {{ results|length }}</p>
            {% set best_model = get_best_model(results) %}
            <p>Best performing model: <strong>{{ best_model[0] }}</strong> with {{ best_model[1]|length }} unique links</p>
        </div>

        {% for model, data in results.items() %}
        <div class="model-section">
            <h2>Model: {{ model }}</h2>
            <p>Total unique links discovered: {{ data.all_links|length }}</p>
            
            <h3>Links discovered across all runs:</h3>
            <table>
                <tr>
                    <th>Link</th>
                    <th>Found in # of runs</th>
                </tr>
                {% for link, count in data.frequency.items() %}
                <tr>
                    <td>{{ link }}</td>
                    <td>{{ count }}/10</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        {% endfor %}
    </body>
    </html>
    """

    # Calculate link frequency for each model
    for model_data in results.values():
        model_data['frequency'] = defaultdict(int)
        for run_links in model_data['runs']:
            for link in run_links:
                model_data['frequency'][link] += 1
        # Convert defaultdict to regular dict
        model_data['frequency'] = dict(model_data['frequency'])

    def get_best_model(results):
        return max(results.items(), key=lambda x: len(x[1]['all_links']))

    # Create the template and render
    template = Template(template)
    html_content = template.render(
        results=results,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        get_best_model=get_best_model
    )

    # Write the report
    with open('benchmark_report.html', 'w') as f:
        f.write(html_content)

def main():
    # Read models from file
    try:
        with open('models.txt', 'r') as f:
            models = [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        print("Error: models.txt file not found!")
        return

    results = {}
    runs_per_model = 10

    for model in models:
        print(f"\nBenchmarking model: {model}")
        model_results = {
            'runs': [],
            'all_links': set()
        }

        for run in range(1, runs_per_model + 1):
            discovered_links = run_fuzzer(model, run, runs_per_model)
            model_results['runs'].append(discovered_links)
            model_results['all_links'].update(discovered_links)
            
            # Small delay between runs
            time.sleep(1)

        results[model] = model_results

    # Generate the HTML report
    generate_html_report(results)
    print("\nBenchmark complete! Report generated as 'benchmark_report.html'")

if __name__ == "__main__":
    main()
