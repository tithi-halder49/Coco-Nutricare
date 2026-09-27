import { getChildren } from "../../services/api";
import { useLoad } from "../../hooks/useLoad";
import ChildrenList from "../../components/ChildrenList";
import { ErrorText, Loader, PageHeader } from "../../components/ui";

export default function ChildrenPage() {
  const { data, loading, error, reload } = useLoad(getChildren);
  return (
    <>
      <PageHeader title="My children" />
      {loading ? <Loader /> : error ? <ErrorText error={error} /> : <ChildrenList kids={data} onAdded={reload} />}
    </>
  );
}
