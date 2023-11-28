def get_package_and_activity(global_d, target_package_name):
    package_activity = global_d.app_current()
    package_name = package_activity['package']
    activity = package_activity['activity']
    return package_name, activity


def stop_app(global_d):
    running_apps = global_d.app_list_running()
    for i in running_apps:
        if i != 'com.github.shadowsocks' and i != 'com.github.uiautomator' and i != 'com.android.systemui' \
                and i != 'com.android.vending' and i != 'com.google.android.gms':
            global_d.app_stop(i)


def stop_other_app(global_d, package_name):
    running_apps = global_d.app_list_running()
    for i in running_apps:
        if i != 'com.github.shadowsocks' and i != package_name and i != 'com.github.uiautomator' \
                and i != 'com.android.systemui' and i != 'com.android.vending' and i != 'com.google.android.gms':
            global_d.app_stop(i)


