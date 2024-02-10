#!/usr/bin/env python3

import re
import argparse
import secrets
import string

indentation = 0
def insertObject(objName:str, **kwargs):
    """Inserts a new object into the database"""
    global indentation
    tabSpace = "  "
    resultString = f"{tabSpace*indentation}{objName} {{\n"
    indentation += 1
    for key, value in kwargs.items():
        k1 = re.sub(r"__\d?$", "", key)
        k1 = k1.replace("_", " ")
        if(k1 == "MYOBJECT"):
            for v in value.split("\n"):
                resultString += f"{tabSpace*indentation}{v}\n"
        else:
            resultString += f"{tabSpace*indentation}{k1} = {value}\n"
    indentation -= 1
    resultString += f"{tabSpace*indentation}}}"
    return resultString

def generatePSW(k:int):
    """Generates a random password of length k"""
    return "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(k))

parser = argparse.ArgumentParser(description='Bacula Configurator \n This script will generate the bacula configuration files based on the given parameters')
parser.add_argument("-dbuser", "--dbuser", type=str, help="Database Login User", required=True)
parser.add_argument("-dbpassword", "--dbpassword", type=str, help="Database Login Password", required=True)
parser.add_argument("-dbhost", "--dbhost", type=str, help="Database Host IP", required=True)
parser.add_argument("-dbport", "--dbport", type=int, help="Database Port", required=True)

parser.add_argument("-gcsbucket", "--gcsbucket", type=str, help="Google Cloud Storage Bucket Name", required=True)
parser.add_argument("-gcsaccesskey", "--gcsaccesskey", type=str, help="Google Cloud Storage Access Key", required=True)
parser.add_argument("-gcssecretkey", "--gcssecretkey", type=str, help="Google Cloud Storage Secret Key", required=True)
parser.add_argument("-gcsregion", "--gcsregion", type=str, help="Google Cloud Storage Region", required=True)

args = parser.parse_args()
if(not args.dbuser or not args.dbpassword or not args.dbhost or not args.dbport or not args.gcsbucket or not args.gcsaccesskey or not args.gcssecretkey or not args.gcsregion):
    parser.print_help()
    exit(1)

dir_pwd = generatePSW(50)

fd_address = "127.0.0.1"
fd_pwd = generatePSW(50)

sd_pwd = generatePSW(50)

dbuser = args.dbuser
dbpassword = args.dbpassword
dbaddress = args.dbhost
dbport = args.dbport

gcs_bucket = args.gcsbucket
gcs_access_key = args.gcsaccesskey
gcs_secret_key = args.gcssecretkey
gcs_region = args.gcsregion

with open("/opt/bacula/etc/modified/bacula-dir.conf", "w") as f:
    f.write(insertObject("Director", Name = "bacula-dir", DIRport = 9101, QueryFile = "\"/opt/bacula/scripts/query.sql\"", WorkingDirectory = "\"/opt/bacula/working\"", PidDirectory = "\"/opt/bacula/working\"", Maximum_Concurrent_Jobs = 20, Password = f"\"{dir_pwd}\"", Messages = "Daemon"))
    f.write(insertObject("JobDefs", Name = "\"DefaultJob\"", Type = "Backup", Level = "Incremental", Client = "bacula-fd", FileSet = "\"Full Set\"", Schedule = "\"WeeklyCycle\"", Storage = "GoogleCloud", Messages = "Standard", Pool = "File",  SpoolAttributes = "yes", Priority = 10, Write_Bootstrap = "\"/opt/bacula/working/%c.bsr\""))
    f.write(insertObject("Job", Name = "\"BackupClient1\"", JobDefs = "\"DefaultJob\""))
    f.write(insertObject("Job", Name = "\"BackupCatalog\"", JobDefs = "\"DefaultJob\"", Level = "Full", FileSet="\"Catalog\"", Schedule = "\"WeeklyCycleAfterBackup\"", RunBeforeJob = "\"/opt/bacula/scripts/make_catalog_backup.pl MyCatalog\"", RunAfterJob  = "\"/opt/bacula/scripts/delete_catalog_backup\"", Write_Bootstrap = "\"/opt/bacula/working/%n.bsr\"", Priority = 11))
    f.write(insertObject("Job", Name = "\"RestoreFiles\"", Type = "Restore", Client = "bacula-fd", Storage = "GoogleCloud", FileSet="\"Full Set\"", Pool = "File", Messages = "Standard", Where = "/tmp/bacula-restores"))
    f.write(insertObject("FileSet", Name = "\"Full Set\"", MYOBJECT__0 = insertObject("Include", MYOBJECT__0 = insertObject("Options",signature = "MD5"), File__0 = "/opt/bacula/sbin"), MYOBJECT__1 = insertObject("Exclude", File__0 = "/opt/bacula/working", File__1 = "/tmp", File__2 = "/proc", File__3 = "/tmp", File__4 = "/sys", File__5 = "/.journal", File__6 = "/.fsck")))
    f.write(insertObject("Schedule", Name = "\"WeeklyCycle\"", Run__0 = "Full 1st sun at 23:05", Run__1 = "Differential 2nd-5th sun at 23:05", Run = "Incremental mon-sat at 23:05"))
    f.write(insertObject("Schedule", Name = "\"WeeklyCycleAfterBackup\"", Run = "Full sun-sat at 23:10"))
    f.write(insertObject("FileSet", Name = "\"Catalog\"", MYOBJECT__0 = insertObject("Include", MYOBJECT__0 = insertObject("Options",signature = "MD5"), File__0 = "\"/opt/bacula/working/bacula.sql\"")))
    f.write(insertObject("Client", Name = "bacula-fd", Address = fd_address, FDPort = 9102, Catalog = "MyCatalog", Password = f"\"{fd_pwd}\"", File_Retention = "60 days", Job_Retention = "6 months", AutoPrune = "yes"))
    f.write(insertObject("Autochanger", Name = "\"GoogleCloud\"", Address = "bacula-sd", SDPort = 9103, Password = f"\"{sd_pwd}\"", Device = "\"GoogleCloudAutoChanger\"", Media_Type = "\"CloudType\"", Maximum_Concurrent_Jobs = 10))
    f.write(insertObject("Catalog", Name = "MyCatalog", dbname = "\"bacula\"", dbuser = f"\"{dbuser}\"", dbpassword = f"\"{dbpassword}\"", dbaddress = f"\"{dbaddress}\"", dbport = dbport))
    f.write(insertObject("Messages", Name = "Standard", mailcommand = "\"/opt/bacula/sbin/bsmtp -h localhost -f \"\(Bacula\) \<%r\>\" -s \"Bacula: %t %e of %c %l\" %r\"", operatorcommand = "\"/opt/bacula/sbin/bsmtp -h localhost -f \"\(Bacula\) \<%r\>\" -s \"Bacula: Intervention needed for %j\" %r\"", mail = "root@localhost = all, !skipped", operator = "root@localhost = mount", console = "all, !skipped, !saved", append = "\"/opt/bacula/log/bacula.log\"" + " = all, !skipped", catalog = "all"))
    f.write(insertObject("Messages", Name = "Daemon", mailcommand = "\"/opt/bacula/sbin/bsmtp -h localhost -f \"\(Bacula\) \<%r\>\" -s \"Bacula daemon message\" %r\"", mail = "root@localhost = all, !skipped", console = "all, !skipped, !saved", append = "\"/opt/bacula/log/bacula.log\"" + " = all, !skipped"))
    f.write(insertObject("Pool", Name = "Default", Pool_Type = "Backup", Recycle = "yes", AutoPrune = "yes", Volume_Retention = "365 days", Maximum_Volume_Bytes = "50G", Maximum_Volumes = 100))
    f.write(insertObject("Pool", Name = "File", Pool_Type = "Backup", Recycle = "yes", AutoPrune = "yes", Volume_Retention = "365 days", Maximum_Volume_Bytes = "50G", Maximum_Volumes = 100, Label_Format = "\"Vol-\""))
    f.write(insertObject("Pool", Name = "Scratch", Pool_Type = "Backup"))

with open("/opt/bacula/etc/modified/bacula-sd.conf", "w") as f:
    f.write(insertObject("Storage", Name = "bacula-sd", SDPort = 9103, WorkingDirectory = "\"/opt/bacula/working\"", PidDirectory = "\"/opt/bacula/working\"", PluginDirectory = "\"/opt/bacula/plugins\"", Maximum_Concurrent_Jobs = 20))
    f.write(insertObject("Director", Name = "bacula-dir", Password = f"\"{sd_pwd}\""))
    f.write(insertObject("Autochanger", Name = "\"GoogleCloudAutoChanger\"", Device = "GoogleCloudStorage", Changer_Command = "\"\"", Changer_Device = "/dev/null"))
    f.write(insertObject("Device", Name = "\"GoogleCloudStorage\"", Device_Type = "\"Cloud\"", Cloud = "\"google-cloud-storage\"", Maximum_Part_Size = "2M", Maximum_File_Size = "2M", Media_Type = "\"CloudType\"", Archive_Device = "\"/tmp\"", LabelMedia = "yes", Random_Access = "yes", AutomaticMount = "yes", RemovableMedia = "no", AlwaysOpen = "no"))
    f.write(insertObject("Cloud", Name="\"google-cloud-storage\"", Driver = "\"S3\"", HostName = "\"storage.googleapis.com\"", BucketName = f"\"{gcs_bucket}\"", AccessKey = f"\"{gcs_access_key}\"", SecretKey = f"\"{gcs_secret_key}\"", Protocol = "HTTPS", UriStyle = "\"Path\"", Truncate_Cache = "\"AfterUpload\"", Upload = "\"EachPart\"", Region = f"\"{gcs_region}\"", MaximumUploadBandwidth = "10MB/s"))
    f.write(insertObject("Messages", Name="Standard", director = "bacula-dir = all"))

with open("/opt/bacula/etc/modified/bconsole.conf", "w") as f:
    f.write(insertObject("Director", Name = "bacula-dir", DIRport = "9101", address = "bacula-dir", Password = f"\"{dir_pwd}\""))