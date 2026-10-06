@live
Feature: Wyoh exposes complete Sway IPC only through an owned development session

  Scenario: Deployment preview cannot manage a service
    Given the Wyoh source is present locally
    When `make wyoh-deploy-preview` runs
    Then it performs only dry-run rsync transfers to the user-owned Pi paths
    And it does not start, stop, enable, disable, or reload a service

  Scenario: A development MCP client uses complete Sway IPC across SSH stdio
    Given `luna-pi` has the pinned Sway 1.10.1 proof prefix and MCP 2.2.0 venv
    And the SSH command starts the MCP server with `--full-ipc-development`
    When a real MCP client discovers every named Sway request and event tool
    And it reads raw Sway state, sends a harmless workspace command, and receives a tick event
    Then every IPC request type is represented by a discoverable named MCP tool
    And subscription event traffic is read through a handle, without a network listener
    And the tool reaches only the owned disposable headless Sway child

  Scenario: The bridge does not attach to a live desktop session
    Given the environment supplies `SWAYSOCK` or `I3SOCK`
    When the entry point is started
    Then it rejects the request before it starts a Sway child or opens an IPC socket

  Scenario: An orderly child exit remains observable
    Given a client subscribes to `shutdown` on the owned child
    When it calls the development-only `wyoh_stop_owned_child_for_test` lifecycle helper
    Then the subscription receives Sway's `shutdown` event
    And stream closure leaves no MCP server, Sway child, subscription socket, port, or service resident

  Scenario: MCP operates the named Sway session that WayVNC presents
    Given `wyoh-sway-vnc.service` owns one loopback-only Sway and WayVNC session
    And it publishes its private session descriptor
    When a real MCP client starts with `--shared-vnc-session`
    And it starts `lxterminal` through Sway IPC
    Then it observes the terminal's Sway window event on that session
    And its screenshot tool writes a server-chosen file path and digest without returning image bytes
    And closing the MCP stream does not stop the persistent Sway/WayVNC service

  # The former "independent VNC client sees the frame change" scenario was
  # withdrawn on 2026-10-04: it captured before the client drew and compared
  # against a stale frame. Its replacement is `minimal_env.feature`.
