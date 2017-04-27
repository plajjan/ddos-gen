

docker-image:
	docker build --build-arg http_proxy=$$http_proxy --build-arg https_proxy=$$https_proxy -t gitlab.dev.terastrm.net:4567/terastream/ddos-gen .

docker-push:
	@docker login -u gitlab-ci-token -p $$CI_BUILD_TOKEN $$CI_REGISTRY
	docker push gitlab.dev.terastrm.net:4567/terastream/ddos-gen
