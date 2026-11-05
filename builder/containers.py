# Container builds mount only the checkout and explicitly selected work and output directories.
from common import require_tools,run


def build(repository,arguments):
    require_tools([arguments.engine])
    tag='amogos-debian-builder:2.1'
    run([arguments.engine,'build','--tag',tag,'--file',repository/'amogos-debian/Containerfile',repository])
    run([arguments.engine,'run','--rm','--privileged','--mount','type=bind,src='+str(repository)+',dst=/source,readonly','--mount','type=bind,src='+str(arguments.work_dir.resolve())+',dst=/work','--mount','type=bind,src='+str(arguments.output_dir.resolve())+',dst=/out',tag,'python3','/source/builder/cli.py','amogos-debian','--work-dir','/work','--output-dir','/out'])
