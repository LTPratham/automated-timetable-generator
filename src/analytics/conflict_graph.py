"""NetworkX Conflict Graph and Chromatic Graph Coloring Visualizer."""

from typing import Dict, List, Tuple
import networkx as nx
import plotly.graph_objects as go
from src.models.entities import SessionVariable, SlotAssignment
from src.models.dataset import DepartmentDataset


def build_conflict_graph(
    dataset: DepartmentDataset,
    assignment: Dict[SessionVariable, SlotAssignment] = None,
) -> nx.Graph:
    """
    Builds a NetworkX graph where:
    - Nodes represent SessionVariables.
    - Edges represent hard constraints (shared faculty or shared batch).
    - Node attributes store course code, faculty, batch, and assigned slot color.
    """
    G = nx.Graph()
    variables = dataset.generate_session_variables()

    for var in variables:
        slot_label = "Unassigned"
        color_code = "#9E9E9E"
        if assignment and var in assignment:
            val = assignment[var]
            slot_label = f"{val.day.value[:3]} S{val.start_slot_index}"
            # Generate deterministic color hue based on day and slot
            hue_id = (dataset.days.index(val.day) * dataset.daily_slots_count + val.start_slot_index)
            color_code = f"hsl({(hue_id * 53) % 360}, 75%, 55%)"

        G.add_node(
            var.variable_id,
            label=f"{var.course_code} ({var.batch_id})",
            course_code=var.course_code,
            faculty_id=var.faculty_id,
            batch_id=var.batch_id,
            session_type=var.session_type.value,
            slot_label=slot_label,
            color=color_code,
        )

    # Add edges for conflicting variables
    num_vars = len(variables)
    for i in range(num_vars):
        v1 = variables[i]
        for j in range(i + 1, num_vars):
            v2 = variables[j]
            reason = []
            if v1.faculty_id == v2.faculty_id:
                reason.append("Faculty Clash")
            if v1.batch_id == v2.batch_id:
                reason.append("Batch Clash")
            if reason:
                G.add_edge(v1.variable_id, v2.variable_id, reason=", ".join(reason))

    return G


def generate_conflict_graph_figure(G: nx.Graph) -> go.Figure:
    """Renders a spring-layout 2D interactive Plotly graph of the conflict network."""
    pos = nx.spring_layout(G, seed=42, k=0.35)

    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=1, color="rgba(160, 160, 160, 0.4)"),
        hoverinfo="none",
        mode="lines",
    )

    node_x = []
    node_y = []
    node_text = []
    node_colors = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        attrs = G.nodes[node]
        node_text.append(
            f"<b>{attrs['course_code']}</b><br>"
            f"Batch: {attrs['batch_id']}<br>"
            f"Faculty: {attrs['faculty_id']}<br>"
            f"Type: {attrs['session_type']}<br>"
            f"Assigned Slot: <b>{attrs['slot_label']}</b>"
        )
        node_colors.append(attrs["color"])

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        hoverinfo="text",
        text=[G.nodes[n]["course_code"] for n in G.nodes()],
        textposition="top center",
        hovertext=node_text,
        marker=dict(
            size=18,
            color=node_colors,
            line=dict(width=2, color="#FFFFFF"),
        ),
    )

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title="<b>Academic Course Conflict Network & Chromatic Slot Allocation</b>",
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=20, r=20, t=50),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor="rgba(240, 242, 246, 0.5)",
            height=600,
        ),
    )
    return fig

