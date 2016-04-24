statusd.inform("battery_template", "0%")

local function inform_battery(bat)
    statusd.inform("battery", tostring(bat))
    nbat = tonumber(bat)
    if nbat < 5 or nbat == 100 then
        statusd.inform("battery_hint", "critical")
    elseif nbat < 15 then
        statusd.inform("battery_hint", "normal") 
    else
        statusd.inform("battery_hint", "important")
    end
end

local battery_timer=statusd.create_timer()

local function update_bat()
    local f = io.popen("acpi | sed 's/%//g' | gawk -F, '{print $2}'", 'r')
    local bat = f:read('*l')
    f:close()
    inform_battery(bat)
    battery_timer:set(10*1000, update_bat)
end

update_bat()
