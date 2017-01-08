import os
import sys
import shutil
from subprocess import Popen

def dependency_check(dependency):
	for path in os.environ["PATH"].split(":"):
		if os.path.isfile(os.path.join(path, dependency)):
			return True
	return False

def ensure_dependencies_installed():
	dependencies = ["exiftool", "jpegoptim"]

	for dependency in dependencies:
		if not dependency_check(dependency):
			print("Dependency " + dependency + " not installed")
			exit()

def parse_args():

	if len(sys.argv) != 2:
		print("Usage: python photosorter.py <DCIM-directory>")
		exit()
	else:
		directory = sys.argv[1]
		if not os.path.isdir(directory):
			print("Error, " + directory + " is not a directory")
			exit()
		else:
			return directory

def redo_directory_structure(directory):

	contents = os.listdir(directory)

	if "CANONMSC" in contents:
		shutil.rmtree(os.path.join(directory, "CANONMSC"))

	if len(contents) == 2 and "Images" in contents and "Videos" in contents:
		return
	else:
		directory_creation = create_directory_structure(directory)
		base, raw, high_jpg, low_jpg, videos = directory_creation

		for folder in contents:

			if folder in ["Images", "Videos", "CANONMSC"]:
				continue
			else:
				folder_dir = os.path.join(directory, folder)
				move_files(folder_dir, raw, high_jpg, videos)

				if len(os.listdir(folder_dir)) != 0:
					print("Directory not empty")
				else:
					shutil.rmtree(folder_dir)

def create_directory_structure(directory):

	base_picture = os.path.join(directory, "Images")
	raw = os.path.join(directory, "Images", "Raw")
	high_quality = os.path.join(directory, "Images", "High Quality")
	low_quality = os.path.join(directory, "Images", "Low Quality")
	videos = os.path.join(directory, "Videos")

	if not os.path.isdir(base_picture):
		os.makedirs(base_picture)
	if not os.path.isdir(raw):
		os.makedirs(raw)
	if not os.path.isdir(high_quality):
		os.makedirs(high_quality)
	if not os.path.isdir(low_quality):
		os.makedirs(low_quality)
	if not os.path.isdir(videos):
		os.makedirs(videos)

	return base_picture, raw, high_quality, low_quality, videos

def move_files(content_dir, raw_dir, jpg_dir, video_dir):

	for image in os.listdir(content_dir):

		image_file = os.path.join(content_dir, image)

		if image.endswith(".CR2"):
			os.rename(image_file, os.path.join(raw_dir, image))
		elif image.endswith(".JPG"):
			os.rename(image_file, os.path.join(jpg_dir, image))
		elif image.endswith(".MP4"):
			os.rename(image_file, os.path.join(video_dir, image))

def convert_missing_jpegs_from_raw(directory):

	jpg_dir = os.path.join(directory, "Images", "High Quality")
	raw_dir = os.path.join(directory, "Images", "Raw")

	jpg_images = os.listdir(jpg_dir)
	raw_images = os.listdir(raw_dir)

	for raw in raw_images:

		image_name = raw.rsplit(".CR2", 1)[0]
		raw_image_file = os.path.join(raw_dir, raw)
		destination_jpg_file = os.path.join(jpg_dir, image_name + ".JPG")

		if not os.path.isfile(destination_jpg_file):						
			convert_raw_to_jpg(raw_image_file, destination_jpg_file)

def convert_raw_to_jpg(raw_source, jpg_destination):

	image_name = os.path.basename(raw_source).rsplit(".CR2", 1)[0]
	raw_dir = os.path.dirname(raw_source)
	generated_jpg_file = os.path.join(raw_dir, image_name + ".jpg")

	exiftool_command = ["exiftool", "-b", "-previewimage", "-w", "jpg"]
	exiftool_command.append(raw_source)

	Popen(exiftool_command).wait()
	os.rename(generated_jpg_file, jpg_destination)

def convert_to_low_quality_jpg(directory):

	high_quality_dir = os.path.join(directory, "Images", "High Quality")
	low_quality_dir = os.path.join(directory, "Images", "Low Quality")

	high_quality_images = os.listdir(high_quality_dir)
	low_quality_images = os.listdir(low_quality_dir)

	for image in high_quality_images:
		if not image in low_quality_images:

			high_quality_image_file = os.path.join(high_quality_dir, image)
			low_quality_image_file = os.path.join(low_quality_dir, image)
			downsize_jpg(high_quality_image_file, low_quality_image_file)

def downsize_jpg(source, destination, size="500k"):
	
	shutil.copyfile(source, destination)
	jpegoptim_command = ["jpegoptim", "--size=" + size, destination]
	Popen(jpegoptim_command).wait()


if __name__ == "__main__":

	ensure_dependencies_installed()
	directory = parse_args()
	redo_directory_structure(directory)
	convert_missing_jpegs_from_raw(directory)
	convert_to_low_quality_jpg(directory)



