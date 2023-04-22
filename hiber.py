#!/usr/bin/env python3
import subprocess, os, math
 
def getSysRam():
    mem_bytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')  # e.g. 4015976448
    mem_gib = mem_bytes/(1024.**3)  # e.g. 3.74
    return mem_gib
 
def run(runCmd):
    output = []
    with subprocess.Popen([runCmd], stdout=subprocess.PIPE, shell=True) as proc:
        print('EXEC: ' + runCmd)
        read = proc.stdout.read().decode('utf-8')
        if(read == ''):
            pass
        else:
            print(read)
            output.extend(read.split('\n'))
    return output
 
run('sudo pacman -Syy')
run('sudo pacman --noconfirm --needed -S linux-zen linux-zen-headers')
run('sudo pacman --noconfirm -R linux linux-headers')
run('yay -S --noconfirm --needed update-grub uswsusp')
run('sudo swapoff -a')
if(os.path.exists('/swapfile')):
    run('sudo rm /swapfile')
    pass
else:
    run('sudo sh -c "echo -e \"/swapfile swap swap defaults 0 0\" >> /etc/fstab"')
 
run('sudo fallocate -l ' + str(math.ceil(getSysRam()) + 2) + 'G /swapfile')
run('sudo chmod 600 /swapfile')
run('sudo mkswap /swapfile')
run('sudo swapon /swapfile')
run('sudo sh -c "echo -e \"add_dracutmodules+=\'resume\'\" > /etc/dracut.conf"')
run('sudo dracut-rebuild')
resumeOffset = run('sudo swap-offset /swapfile')[0].split(' ')[3]
uuid = run('findmnt -no UUID -T /swapfile')[0]
run('sudo sed -i "s/loglevel=3\'/loglevel=3 resume=UUID=' + uuid + ' resume_offset=' + resumeOffset + '\'/g" /etc/default/grub')
run('sudo update-grub')
run('sudo mkdir -p /etc/systemd/system/systemd-logind.service.d/')
run('sudo sh -c "echo -e \"[Service]\" > /etc/systemd/system/systemd-logind.service.d/override.conf"')
run('sudo sh -c "echo -e \"Environment=SYSTEMD_BYPASS_HIBERNATION_MEMORY_CHECK=1\" >> /etc/systemd/system/systemd-logind.service.d/override.conf"')
print('Done')