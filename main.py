from subprocess import run,PIPE,Popen,check_output
import os,sys,logging

bins=[
    'bash',
    'mkdir',
    'rm',
    'ls',
    'cd',
    'nano',
    'cat',
    'echo',
    'clear',
    'g++',
    'vim',
    'ps',
    'python3',
    'mount',
    'mv',
    'cp',
    'umount',
    'env',
    'top'
]

chroot_dir=f"{os.getcwd()}/chroot"
print(f"Chroot dir is {chroot_dir}\n")

bin_paths=[]
lib_paths=[]
paths=[]
for b in bins:
    cmd=run(['which',b],stdout=PIPE)
    path=cmd.stdout.decode('utf-8').split('\n')[0]
    bin_paths.append(path)
    print(f"Bin {b}'s path is {path}")
    # Get deps with command "ldd bin_name | awk 'NF == 4 {print $3}; NF == 2 {print $1}'"
    ldd = Popen(('ldd', path), stdout=PIPE)
    output = check_output(('awk', 'NF == 4 {print $3}; NF == 2 {print $1}'), stdin=ldd.stdout)
    ldd.wait()

    deps=output.decode('utf-8').split('\n')
    deps.pop(-1)
    lib_paths.extend(deps)
    print("Deps added")
print("\nRemoving duplicates...")
new_lib_paths=[]
for i in lib_paths:
    if not i in new_lib_paths:
        new_lib_paths.append(i)
print("Done\n")
paths.extend(bin_paths)
paths.extend(new_lib_paths)


input("About to copy all files (bins and deps) to chroot, press enter to continue, press ctrl+c to exit. ")
print("\nCopying files...\n")
for b in paths:
    dst=chroot_dir+b
    dst_dir=dst.split('/')
    dst_dir.pop(-1)
    dst_dir="/".join(dst_dir)
    run(['mkdir','-p',dst_dir])
    err=run(['cp',b,dst_dir],stderr=PIPE).stderr
    if err:
        print(f"Error running cp {b} {dst_dir}: {err.decode('utf-8')}")
    else:
        print(f"Copied {b} to {dst}")
