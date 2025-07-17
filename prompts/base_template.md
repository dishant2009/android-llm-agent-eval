You are an expert Android user.

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

Provide the next action in the exact format specification. Only output the action string. 