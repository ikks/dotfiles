mod_statusbar.create{
    screen=0,
    pos='bl',
    fullsize=false,
    systray=true,

    template="[ %date || load: %load || %battery%% || %wireless ] %filler%systray",
}


mod_statusbar.launch_statusd{
    date={
        date_format='%a %Y-%m-%d %H:%M',
        formats={ 
            time = '%H:%M', -- %date_time
        }
    },      

    load={
        --update_interval=10*1000,
        --important_threshold=1.5,
        --critical_threshold=4.0,
    },

    -- Make sure you have ~/.notion/statusd_battery.lua
    battery={
        program = "acpi | gawk -F, '{print $2}' | sed 's/%//g'",
        retry_delay = 5 * 1000,
    },

    -- Make sure you have ~/.notion/statusd_wireless.lua
    wireless={
        program = "ip a | grep wlp2s0 | grep \"state UP\" >> /dev/null && echo Y || echo X",
        retry_delay = 5 * 1000,
    },
}

