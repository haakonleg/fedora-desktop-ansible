table.insert (bluez_monitor.rules, {
  matches = {
    {
      -- Matches all sources.
      { "node.name", "matches", "bluez_input.*" },
    },
    {
      -- Matches all sinks.
      { "node.name", "matches", "bluez_output.*" },
    },
  },
  apply_properties = {
    ["session.suspend-timeout-seconds"] = 0,  -- 0 disables suspend
  },
})
