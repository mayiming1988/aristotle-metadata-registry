prepare_server:
	django-admin migrate
	django-admin compile_and_collect_static
	django-admin load_aristotle_help

metadata:
	django-admin loaddata test_metadata.json

server:
	sudo docker-compose up

elasticsearch_work:
	sudo sysctl -w vm.max_map_count=262144
esw:
	sudo sysctl -w vm.max_map_count=262144
