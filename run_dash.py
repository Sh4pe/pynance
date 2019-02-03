if __name__ == "__main__":
    from pynance.dash_viz import plot_flow

    app = plot_flow.app
    app.run_server(debug=True)
