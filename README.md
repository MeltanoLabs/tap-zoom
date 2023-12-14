# `tap-zoom`

`tap-zoom` is a Singer tap for [Zoom](https://zoom.com/).

Built with the [Meltano Singer SDK](https://sdk.meltano.com).

## Capabilities

* `catalog`
* `state`
* `discover`
* `about`
* `stream-maps`
* `schema-flattening`

## Settings

| Setting             | Required | Default | Description |
|:--------------------|:--------:|:-------:|:------------|
| account_id          | True     | None    | The ID of the account. |
| client_id           | True     | None    | The OAuth application's Client ID. |
| client_secret       | True     | None    | The OAuth application's Client Secret. |
| api_url             | False    | None    | Override the url for the API service. |
| start_date          | False    | None    | The earliest record date to sync |
| stream_config       | False    | None    | A list of dictionaries for specifing additional             configurations for a specified stream. |
| stream_maps         | False    | None    | Config object for stream maps capability. For more information check out [Stream Maps](https://sdk.meltano.com/en/latest/stream_maps.html). |
| stream_map_config   | False    | None    | User-defined config values to be used within map expressions. |
| flattening_enabled  | False    | None    | 'True' to enable schema flattening and automatically expand nested properties. |
| flattening_max_depth| False    | None    | The max depth to flatten schemas. |

A full list of supported settings and capabilities is available by running: `tap-zoom --about`

### Settings for Specific Streams

Settings can be added on a per-stream basis and can be set using the stream_config setting. The stream_config setting takes a list of dictionaries, requiring the stream name as a value in the stream key. If the same stream name is added multiple times, only the last will be used.

| Setting             | Required | Default | Description |
|:--------------------|:--------:|:-------:|:------------|
| stream              | True     | None    | Name of the stream to configure |
| parameters          | False    | None    | URL query string to send to the stream endpoint |

Example:

```json
{
    "stream_config": [
        {
            "stream": "STREAM_NAME",
            "parameters": "URL_QUERY_STRING"
        }
    ]
}
```

### Configure using environment variables

This Singer tap will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

### Source Authentication and Authorization

<!--
Developer TODO: If your tap requires special access on the source system, or any special authentication requirements, provide those here.
-->

## Usage

You can easily run `tap-zoom` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-zoom --version
tap-zoom --help
tap-zoom --config CONFIG --discover > ./catalog.json
```

## Developer Resources

Follow these instructions to contribute to this project.

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tap_zoom/tests` subfolder and
  then run:

```bash
poetry run pytest
```

You can also test the `tap-zoom` CLI interface directly using `poetry run`:

```bash
poetry run tap-zoom --help
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

<!--
Developer TODO:
Your project comes with a custom `meltano.yml` project file already created. Open the `meltano.yml` and follow any "TODO" items listed in
the file.
-->

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
pipx install meltano
# Initialize meltano within this directory
cd tap-zoom
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-zoom --version
# OR run a test `elt` pipeline:
meltano elt tap-zoom target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to develop your own taps and targets.
