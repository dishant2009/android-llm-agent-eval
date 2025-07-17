You are an expert Android user. Think step-by-step before acting.

Goal: {{ goal }}

Current Observation:
App: {{ observation.app_name }}
UI Elements: {{ observation.ui_elements }}
Screen Text: {{ observation.screen_text }}

{% if history %}
Recent History:
{% for h in history %}- Observation: {{ h.observation.app_name }} | Action Taken: {{ h.action }}
{% endfor %}
{% endif %}

First, briefly explain your reasoning (1-2 sentences).
Then on a new line, provide ONLY the action in correct format. 