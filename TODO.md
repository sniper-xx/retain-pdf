# TODO

## Docker Release Follow-up

- [ ] Run a full app image build with the updated Rust toolchain:
  `docker build -f docker/Dockerfile.app -t retainpdf-app:test .`
- [ ] Run the local compose build path:
  `cd docker/delivery && docker compose -f docker-compose.yml -f docker-compose.build.yml up -d --build`
- [ ] Smoke test the local deployment at `http://127.0.0.1:40001`.
- [ ] Verify the generated web `runtime-config.js` includes `ocrProvider`, `paddleToken`, and `deepseek-v4-flash`.
- [ ] Push refreshed Docker Hub images with an explicit version tag:
  `docker/release-images.sh v4.1.0`
- [ ] Confirm Docker Hub `latest` was updated after release:
  `gh repo view wxyhgk/retain-pdf --web`

## Notes

- The default compose file still pulls Docker Hub images.
- Use `docker-compose.build.yml` when deploying directly from the current source tree.
- The app Docker build now defaults to Rust `1.88`, because the current locked Rust dependencies require it.
