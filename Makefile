default:
	docker build --rm=true -t github/ghtop .
	docker run --rm -ti --name ghtop github/ghtop python ghtop.py ${ghtop}
