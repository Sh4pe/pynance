if __name__ == "__main__":
    from pynance.dash_viz import plot_flow
    import webbrowser

    app = plot_flow.app

    port = 8050

    url = "http://localhost:%s" % int(port)
    webbrowser.open_new_tab(url)

    app.run_server(port=port)
