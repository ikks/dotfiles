statusd.inform("wireless_template", "0%")

local function inform_wireless(status)
    statusd.inform("wireless", tostring(status))
    if status == "X" then
        statusd.inform("wireless_hint", "critical")
    else
        statusd.inform("wireless_hint", "important")
    end
end

local wireless_timer=statusd.create_timer()

local function update_wir()
    local f = io.popen("ip a | grep wlp2s0 | grep \"state UP\" >> /dev/null && echo Y || echo X", 'r')
    local wir = f:read('*l')
    f:close()
    inform_wireless(wir)
    wireless_timer:set(10*1000, update_wir)
end

update_wir()
